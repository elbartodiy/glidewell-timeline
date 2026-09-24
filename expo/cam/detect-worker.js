/* THE MODELS LIVE HERE, OFF THE PAGE'S THREAD.
   On the page itself the pose model cost 11 ms a call even on the M3's GPU —
   the GPU delegate still waits for its result — and 20+ ms at start; the hall
   would drop a frame at every detection (measured 2026-09-24). In a worker
   that wait is nobody's frame. The page sends an ImageBitmap of the current
   video frame and gets back only numbers: landmarks and smile scores.
   A classic worker, because the loader MediaPipe ships uses importScripts. */
importScripts('vendor/vision_bundle.js');
const V = self.Vision;
const FILESET = {wasmLoaderPath: new URL('vendor/wasm/vision_wasm_internal.js', location.href).href,
                 wasmBinaryPath: new URL('vendor/wasm/vision_wasm_internal.wasm', location.href).href};
let pose = null, face = null, delegate = '';

async function make(Cls, model, extra){
  for (const d of ['GPU', 'CPU']){
    try {
      const t = await Cls.createFromOptions(FILESET, Object.assign({
        baseOptions: {modelAssetPath: new URL('vendor/' + model, location.href).href, delegate: d},
        runningMode: 'VIDEO'}, extra));
      delegate = d; return t;
    } catch(e){ if (d === 'CPU') throw e; }
  }
}

self.onmessage = async ({data: m}) => {
  try {
    if (m.type === 'init'){
      if (m.pose && !pose) pose = await make(V.PoseLandmarker, 'pose_landmarker_lite.task', {numPoses: m.maxPeople});
      if (m.face && !face) face = await make(V.FaceLandmarker, 'face_landmarker.task',
                                             {numFaces: m.maxPeople, outputFaceBlendshapes: true});
      self.postMessage({type: 'ready', delegate});
      return;
    }
    if (m.type === 'frame'){
      const t0 = performance.now();
      let poses = [], faces = [];
      if (pose) poses = (pose.detectForVideo(m.bitmap, m.ts).landmarks || [])
        .map(lm => lm.map(p => ({x: p.x, y: p.y, visibility: p.visibility})));
      if (face){
        const r = face.detectForVideo(m.bitmap, m.ts);
        faces = (r.faceLandmarks || []).map((lm, i) => {
          const bs = r.faceBlendshapes && r.faceBlendshapes[i] ? r.faceBlendshapes[i].categories : [];
          const g = n => (bs.find(c => c.categoryName === n) || {score: 0}).score;
          return {x: lm[1].x, y: lm[1].y, smile: (g('mouthSmileLeft') + g('mouthSmileRight')) / 2};
        });
      }
      m.bitmap.close();
      self.postMessage({type: 'result', poses, faces, ms: performance.now() - t0});
    }
  } catch(e){
    if (m.bitmap) try { m.bitmap.close(); } catch(_){}
    self.postMessage({type: 'error', error: String(e.message || e)});
  }
};
