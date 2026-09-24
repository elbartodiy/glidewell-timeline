/* VISITOR CAM — the camera in front of the hall, as something a page can ask.

   One module for the hall and for every other interactive piece (the arcade
   games, the lab stands): it owns the picture and what is seen in it, and
   answers in plain terms — how many people, who is near, who raised a hand,
   who is smiling — plus the live video itself, for drawing into a scene.

   THE PICTURE comes from one of three places, chosen by `src`:
     'tapo'            the Tapo C113 through the local bridge (go2rtc, see
                       bridge/README.md): RTSP from the camera → WebRTC here.
                       The bridge answers on http://127.0.0.1:1984.
     'webcam'          this computer's own camera — for developing on the Mac.
     'file:<url>'      a video file on a loop — to test detection with nobody
                       in front of the camera (a speaker clip from media/ has
                       a person in it; Eldar, 2026-09-24).
   'tapo:<stream>' picks another bridge stream (tapo_sd is the 640×360 one).

   WHAT IS SEEN runs on MediaPipe in a worker (detect-worker.js), served from
   vendor/ next to this file and never from a CDN: an exhibition floor has no reliable internet. The pose
   model (lite) finds up to four bodies; the face model is loaded only when a
   page asks for smiles. Detection runs a few times a second, not per frame —
   people move slowly compared to 60 fps, and the hall's frame budget is the
   hall's.

   NOTHING IS STORED: no frame leaves this page unless a page asks for a
   snapshot on purpose. Counts go to localStorage as numbers only.

   Usage:
     const {VisitorCam} = await import('./cam/visitor-cam.js');
     const cam = await VisitorCam.start({src: 'webcam', debug: true});
     cam.on('arrive', p => …);   // someone came NEAR (new track crossed the line)
     cam.on('leave', () => …);   // nobody near for `emptyHold` seconds
     cam.on('raise', p => …);    // a hand went above the head (edge, not level)
     cam.on('smile', p => …);    // face mode only
     cam.people                  // [{id, x, y, size, near, raised, smile, lm}]
     cam.near, cam.count, cam.emptyFor, cam.arrivals
     cam.video                   // HTMLVideoElement, drawable into a canvas
     cam.snapshot(w)             // a canvas with the current frame, mirrored
*/

const BASE = new URL('.', import.meta.url).href;

const DEFAULTS = {
  src: 'webcam',
  bridge: 'http://127.0.0.1:1984',
  fps: 8,              // detections per second
  pose: true,
  face: false,         // smiles; costs a second model
  maxPeople: 4,
  /* NEAR is a shoulder width, as a fraction of the frame width. The C113's
     lens is wide (≈100° across): shoulders of 0.45 m read ≈0.19 of the frame
     at 1 m and ≈0.09 at 2 m. 0.10 is "about two metres from the camera" — the
     distance at which a person is looking at the screen, not walking past it.
     It depends on where the camera is mounted, so it is a parameter (?camnear=). */
  near: 0.10,
  born: 0.8,           // s a body must persist before it is a visitor
  lost: 2.0,           // s a track survives without being seen
  emptyHold: 6,        // s with nobody near before 'leave'
  mirror: true,        // the camera faces the visitor: flip, so left is left
  debug: false,
  statsKey: null,      // localStorage key for the daily counter; null = off
};

/* ── the picture ───────────────────────────────────────────────────────── */
async function openWebcam(video){
  const s = await navigator.mediaDevices.getUserMedia({video: {width: 1280, height: 720}, audio: false});
  video.srcObject = s;
  return () => s.getTracks().forEach(t => t.stop());
}
async function openFile(video, url){
  video.src = url; video.loop = true; video.crossOrigin = 'anonymous';
  return () => { video.removeAttribute('src'); video.load(); };
}
/* go2rtc takes a raw SDP offer by POST and answers with raw SDP — no
   signalling library needed. Gathering finishes before the offer goes, since
   the bridge does not trickle. */
async function openBridge(video, bridge, stream){
  const pc = new RTCPeerConnection();
  pc.addTransceiver('video', {direction: 'recvonly'});
  pc.ontrack = e => { video.srcObject = e.streams[0] || new MediaStream([e.track]); };
  await pc.setLocalDescription(await pc.createOffer());
  await new Promise(res => {
    if (pc.iceGatheringState === 'complete') return res();
    const t = setTimeout(res, 1500);
    pc.addEventListener('icegatheringstatechange', () => {
      if (pc.iceGatheringState === 'complete'){ clearTimeout(t); res(); }
    });
  });
  const r = await fetch(`${bridge}/api/webrtc?src=${encodeURIComponent(stream)}`,
                        {method: 'POST', body: pc.localDescription.sdp});
  if (!r.ok) throw new Error(`bridge ${r.status}: ${(await r.text()).slice(0, 120)}`);
  await pc.setRemoteDescription({type: 'answer', sdp: await r.text()});
  return () => pc.close();
}

/* ── the models run in detect-worker.js: see why there ─────────────────── */

/* ── the counter ───────────────────────────────────────────────────────── */
function dayKey(d){ return d.toISOString().slice(0, 10); }
function loadStats(key){ try { return JSON.parse(localStorage.getItem(key) || '{}'); } catch(e){ return {}; } }
function saveStats(key, s){ try { localStorage.setItem(key, JSON.stringify(s)); } catch(e){} }

/* ── the camera ────────────────────────────────────────────────────────── */
class Cam {
  constructor(opts){
    this.o = Object.assign({}, DEFAULTS, opts);
    this.state = 'off'; this.error = '';
    this.people = []; this.near = 0; this.count = 0;
    this.emptyFor = 0; this.arrivals = 0; this.detectMs = 0;
    this._h = {}; this._tracks = []; this._nextId = 1; this._lastSeenNear = performance.now();
    this._left = true;
    const v = document.createElement('video');
    v.muted = true; v.playsInline = true; v.autoplay = true;
    this.video = v;
  }
  on(ev, fn){ (this._h[ev] = this._h[ev] || []).push(fn); return this; }
  _emit(ev, a){ for (const f of this._h[ev] || []) { try { f(a); } catch(e){ console.error(e); } } }

  async _open(){
    const s = this.o.src;
    this.state = 'connecting'; this.error = '';
    try {
      if (this._close) { this._close(); this._close = null; }
      if (s === 'webcam') this._close = await openWebcam(this.video);
      else if (s.startsWith('file:')) this._close = await openFile(this.video, s.slice(5));
      else if (s.startsWith('tapo')) this._close = await openBridge(this.video, this.o.bridge, s.split(':')[1] || 'tapo');
      else throw new Error('unknown src ' + s);
      await this.video.play().catch(() => {});
      this.state = 'live';
    } catch(e){
      this.state = 'error'; this.error = String(e.message || e);
      console.warn('[visitor-cam]', this.error);
    }
  }

  /* THE WATCHDOG. A show runs for days; a Wi-Fi camera drops out and comes
     back. If no new frame has arrived for five seconds the picture is
     reopened, with a growing pause, and the page never has to know. */
  _watch(){
    let lastT = -1, stale = 0, wait = 2;
    setInterval(async () => {
      const t = this.video.currentTime;
      if (this.state === 'live' && this.video.paused) this.video.play().catch(() => {});
      if (this.state === 'live' && t !== lastT){ lastT = t; stale = 0; wait = 2; return; }
      stale += 1;
      if (stale >= (this.state === 'live' ? 5 : wait) && this.state !== 'connecting'){
        stale = 0; wait = Math.min(30, wait * 2);
        await this._open();
      }
    }, 1000);
  }

  async start(){
    await this._open();
    this._watch();
    this.worker = new Worker(BASE + 'detect-worker.js');
    this._busy = false;
    this.worker.onmessage = ({data: m}) => {
      if (m.type === 'ready'){ this.delegate = m.delegate; this._ready = true; }
      else if (m.type === 'result'){
        this._busy = false;
        this.detectMs = this.detectMs ? this.detectMs * 0.8 + m.ms * 0.2 : m.ms;
        this._update(m.poses, m.faces, performance.now());
      }
      else if (m.type === 'error'){ this._busy = false; this.error = 'detect: ' + m.error; }
    };
    this.worker.postMessage({type: 'init', pose: this.o.pose, face: this.o.face, maxPeople: this.o.maxPeople});
    this._loop();
    if (this.o.debug) this._debug();
    if (this.o.statsKey) this._statsTick();
    return this;
  }
  wantFace(){
    this.o.face = true;
    if (this.worker) this.worker.postMessage({type: 'init', face: true, maxPeople: this.o.maxPeople});
  }

  /* one frame in flight at a time: if the worker is still busy, this tick is
     skipped rather than queued — a queue would only report the past */
  _loop(){
    let lastVT = -1, lastTs = 0;
    const tick = async () => {
      setTimeout(tick, 1000 / this.o.fps);
      const v = this.video;
      if (!this._ready || this._busy || this.state !== 'live' || v.readyState < 2 || !v.videoWidth) return;
      if (v.currentTime === lastVT) return;      // no new frame, nothing new to see
      lastVT = v.currentTime;
      this._busy = true;
      try {
        // 640 across is plenty: the pose model itself looks at 256
        const bitmap = await createImageBitmap(v, {resizeWidth: 640,
          resizeHeight: Math.round(640 * v.videoHeight / v.videoWidth), resizeQuality: 'low'});
        const ts = lastTs = Math.max(lastTs + 1, Math.round(performance.now()));
        this.worker.postMessage({type: 'frame', bitmap, ts}, [bitmap]);
      } catch(e){ this._busy = false; }
    };
    tick();
  }

  /* bodies → people: the landmark numbers are MediaPipe's pose topology
     (0 nose, 11/12 shoulders, 15/16 wrists, 23/24 hips) */
  _body(lm){
    const vis = i => (lm[i].visibility == null ? 1 : lm[i].visibility) > 0.5;
    const X = x => this.o.mirror ? 1 - x : x;
    const sh = vis(11) && vis(12) ? Math.hypot(lm[11].x - lm[12].x, lm[11].y - lm[12].y) : 0;
    const head = lm[0];
    const cx = sh ? (lm[11].x + lm[12].x) / 2 : head.x;
    const up = w => vis(w) && vis(0) && lm[w].y < head.y - sh * 0.3;
    return {x: X(cx), y: head.y, size: sh, near: sh >= this.o.near,
            raised: (up(15) || up(16)) ? (up(15) && up(16) ? 'both' : 'one') : '',
            head: {x: X(head.x), y: head.y}, lm};
  }

  /* TRACKS. A visitor is a body that stays: it is born after `born` seconds
     and dies `lost` seconds after it was last seen, so one person turning
     round, or hidden for a moment by another, is still one person. Matching
     is nearest centre, which is all four people need. */
  _update(poses, faces, now){
    const bodies = poses.map(lm => this._body(lm));
    for (const f of faces){          // a smile belongs to the nearest head
      const fx = this.o.mirror ? 1 - f.x : f.x;
      let best = null, bd = 0.15;
      for (const b of bodies){ const d = Math.hypot(b.head.x - fx, b.head.y - f.y); if (d < bd){ bd = d; best = b; } }
      if (best) best.smile = f.smile;
    }
    const free = new Set(this._tracks);
    for (const b of bodies){
      let best = null, bd = 0.25;
      for (const t of free){ const d = Math.hypot(t.x - b.x, t.y - b.y); if (d < bd){ bd = d; best = t; } }
      if (!best){ best = {id: 0, first: now, wasNear: false, raised: '', smiling: false}; this._tracks.push(best); }
      else free.delete(best);
      Object.assign(best, b, {seen: now});
    }
    this._tracks = this._tracks.filter(t => now - t.seen < this.o.lost * 1000);
    const live = [];
    for (const t of this._tracks){
      if (!t.id && now - t.first >= this.o.born * 1000){
        t.id = this._nextId++;
        this._stat(s => s.visitors = (s.visitors || 0) + 1);
      }
      if (!t.id) continue;
      const fresh = now - t.seen < 300;
      if (fresh && t.near && !t.wasNear){
        t.wasNear = true; this.arrivals++;
        this._stat(s => s.engaged = (s.engaged || 0) + 1);
        this._emit('arrive', t);
      }
      if (fresh && t.raised && !t.wasRaised) this._emit('raise', t);
      t.wasRaised = fresh && !!t.raised;
      if (fresh && (t.smile || 0) > 0.55 && !t.smiling){ t.smiling = true; this._emit('smile', t); }
      if ((t.smile || 0) < 0.3) t.smiling = false;
      if (fresh) live.push(t);
    }
    this.people = live;
    this.count = live.length;
    this.near = live.filter(p => p.near).length;
    if (this.near) { this._lastSeenNear = now; this._left = false; }
    this.emptyFor = (now - this._lastSeenNear) / 1000;
    if (!this._left && this.emptyFor >= this.o.emptyHold){ this._left = true; this._emit('leave'); }
    this._stat(s => s.peak = Math.max(s.peak || 0, this.count), true);
    this._emit('frame', this);
  }

  snapshot(w = 1280){
    const v = this.video, c = document.createElement('canvas');
    if (!v.videoWidth) return null;
    c.width = w; c.height = Math.round(w * v.videoHeight / v.videoWidth);
    const g = c.getContext('2d');
    if (this.o.mirror){ g.translate(c.width, 0); g.scale(-1, 1); }
    g.drawImage(v, 0, 0, c.width, c.height);
    return c;
  }

  /* ── the daily counter: visitors (bodies that stayed), engaged (came near),
     time spent near, the busiest hour. Numbers only. ── */
  _stat(fn, quiet){
    if (!this.o.statsKey) return;
    const all = this._stats || (this._stats = loadStats(this.o.statsKey));
    const d = dayKey(new Date());
    fn(all[d] = all[d] || {});
    if (!quiet) this._dirty = true;
  }
  _statsTick(){
    setInterval(() => {
      if (this.near) this._stat(s => {
        s.nearSec = (s.nearSec || 0) + 1;
        const h = new Date().getHours();
        (s.hours = s.hours || {})[h] = (s.hours[h] || 0) + 1;
      });
      if (this._stats) saveStats(this.o.statsKey, this._stats);
    }, 1000);
  }
  extra(key, n = 1){ this._stat(s => (s.extra = s.extra || {})[key] = (s.extra[key] || 0) + n); }

  /* ── the debug window: the picture as the model sees it, every body with
     its shoulder line (green = near), the near line's size, and the numbers.
     A separate little canvas over the page, so it touches nothing of the
     page's own drawing. ── */
  _debug(){
    const c = document.createElement('canvas');
    c.width = 360; c.height = 250;
    c.style.cssText = 'position:fixed;right:12px;bottom:12px;z-index:99999;border-radius:8px;' +
                      'background:#05080c;box-shadow:0 4px 24px rgba(0,0,0,.5);pointer-events:none';
    document.body.appendChild(c);
    const g = c.getContext('2d');
    const draw = () => {
      requestAnimationFrame(draw);
      const v = this.video, W = c.width, Hv = 202;
      g.fillStyle = '#05080c'; g.fillRect(0, 0, W, c.height);
      if (v.videoWidth){
        const s = Math.min(W / v.videoWidth, Hv / v.videoHeight);
        const w = v.videoWidth * s, h = v.videoHeight * s, ox = (W - w) / 2;
        g.save();
        if (this.o.mirror){ g.translate(ox + w, 0); g.scale(-1, 1); } else g.translate(ox, 0);
        g.globalAlpha = 0.85; g.drawImage(v, 0, 0, w, h); g.restore();
        for (const p of this.people){
          const P = i => [ox + (this.o.mirror ? 1 - p.lm[i].x : p.lm[i].x) * w, p.lm[i].y * h];
          g.strokeStyle = p.near ? '#5de08a' : '#e8b04a'; g.lineWidth = 3;
          g.beginPath(); g.moveTo(...P(11)); g.lineTo(...P(12)); g.stroke();
          g.lineWidth = 1.5;
          for (const [a, b] of [[11,13],[13,15],[12,14],[14,16],[11,23],[12,24]]){
            g.beginPath(); g.moveTo(...P(a)); g.lineTo(...P(b)); g.stroke();
          }
          const [hx, hy] = P(0);
          g.fillStyle = g.strokeStyle; g.font = '600 12px ui-monospace,Menlo,monospace';
          g.fillText(`#${p.id} ${(p.size * 100).toFixed(0)}%${p.raised ? ' ✋' : ''}${p.smiling ? ' ☺' : ''}`, hx - 20, Math.max(12, hy - 14));
        }
        // the near line, drawn as a shoulder width
        g.strokeStyle = 'rgba(93,224,138,.6)'; g.lineWidth = 2;
        g.beginPath(); g.moveTo(8, Hv - 8); g.lineTo(8 + this.o.near * w, Hv - 8); g.stroke();
      }
      g.fillStyle = this.state === 'live' ? '#9fdcff' : '#ff9a7a';
      g.font = '12px ui-monospace,Menlo,monospace';
      g.fillText(`${this.o.src} · ${this.state}${this.error ? ' · ' + this.error.slice(0, 34) : ''}`, 8, Hv + 18);
      g.fillStyle = '#cfe6f5';
      g.fillText(`people ${this.count}  near ${this.near}  arrivals ${this.arrivals}  empty ${this.emptyFor.toFixed(0)}s  ${this.detectMs.toFixed(0)}ms ${this.delegate || ''}`, 8, Hv + 36);
    };
    draw();
  }
}

function statsCSV(key){
  const s = loadStats(key);
  const rows = [['date', 'visitors', 'engaged', 'near_minutes', 'peak_together', 'busiest_hour', 'extra']];
  for (const d of Object.keys(s).sort()){
    const r = s[d], hs = r.hours || {}, ex = r.extra || {};
    const bh = Object.keys(hs).sort((a, b) => hs[b] - hs[a])[0];
    const extra = Object.keys(ex).sort((a, b) => ex[b] - ex[a]).map(k => `${k} ${ex[k]}`).join('; ');
    rows.push([d, r.visitors || 0, r.engaged || 0, ((r.nearSec || 0) / 60).toFixed(1), r.peak || 0,
               bh == null ? '' : bh + ':00', '"' + extra.replace(/"/g, '""') + '"']);
  }
  return rows.map(r => r.join(',')).join('\n');
}

export const VisitorCam = {
  async start(opts){ const c = new Cam(opts); window.VCAM = c; return c.start(); },
  stats: loadStats,
  statsCSV,
  downloadCSV(key, name){
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob(['\ufeff' + statsCSV(key)], {type: 'text/csv;charset=utf-8'}));
    a.download = `${name}_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
  },
  /* the query string, read the same way everywhere: ?cam=webcam|tapo|file:…
     remembered on this machine until ?cam=off, so the show computer keeps its
     camera across restarts without a special address */
  fromQuery(storeKey = 'vcam.src'){
    const q = new URLSearchParams(location.search);
    let src = q.get('cam');
    try {
      if (src === 'off'){ localStorage.removeItem(storeKey); return null; }
      if (src) localStorage.setItem(storeKey, src);
      else src = localStorage.getItem(storeKey);
    } catch(e){}
    if (!src) return null;
    const o = {src, debug: q.has('camdbg')};
    if (q.get('camnear')) o.near = parseFloat(q.get('camnear'));
    if (q.get('camfps')) o.fps = parseFloat(q.get('camfps'));
    if (q.get('bridge')) o.bridge = q.get('bridge');
    if (q.has('camface')) o.face = true;
    return o;
  },
};
