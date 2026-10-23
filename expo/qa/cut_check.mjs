#!/usr/bin/env node
/* Проверка сдвига зала: всё ли едет вместе с врезкой.

   Зал загружается дважды — как есть и с пробной врезкой из адреса
   (?cut=AT:W, см. CUTS в expo.html), — и сравнивается мировое положение всего,
   что стоит в зале: годы, прилавки и разрывы, бухты, предметы, снимки на стенах,
   экраны фильма, лампы, проекторы. Правило одно: всё, что правее места врезки,
   должно уехать ровно на W, всё левее — остаться на месте. Нарушитель — это вещь,
   записанная абсолютным числом или привязанная не к тому соседу; его и надо
   чинить, прежде чем резать зал по-настоящему (23.10.2026, после вырезки trim73:
   синяя комната 80-х осталась на месте, потому что её края были написаны
   числами 10 390 и 13 557).

       node expo/qa/cut_check.mjs 4000 -402          # проба: raw-координата и ширина
       node expo/qa/cut_check.mjs 4000 -402 8777     # порт уже запущенного сервера

   Нужен headless Chrome с отладкой на 9388:
     Chrome --headless=old --mute-audio --remote-debugging-port=9388 --user-data-dir=/tmp/cr_sw
   и сервер репозитория (python3 -m http.server 8777 в корне). */
const [AT, WD, PORT = '8777'] = process.argv.slice(2);
if (AT == null || WD == null){ console.error('usage: cut_check.mjs AT W [port]'); process.exit(2); }
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function page(){
  const list = await (await fetch('http://127.0.0.1:9388/json/list')).json();
  const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
  await new Promise(r => ws.addEventListener('open', r, {once: true}));
  let id = 0; const wait = new Map();
  ws.addEventListener('message', m => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)){ wait.get(d.id)(d); wait.delete(d.id); } });
  const call = (method, params = {}) => new Promise(r => { const i = ++id; wait.set(i, r); ws.send(JSON.stringify({id: i, method, params})); });
  return {call, close: () => ws.close()};
}

/* всё, у чего есть мировое x; ключ — устойчивое имя, не номер в массиве, где
   это возможно */
const DUMP = `(() => {
  const o = {};
  const put = (k, x) => { if (x != null && isFinite(x)) o[k] = +x; };
  BEATS.forEach(b => { const k = 'beat ' + b.y + ' ' + (b.t || '');
    put(k, b.x);
    (b.wall || []).forEach(w => put(k + ' · wall ' + (w.img || ''), b.x + (w.dx || 0)));
    (b.st || []).forEach(w => put(k + ' · stand ' + (w.img || ''), b.x + (w.dx || 0)));
  });
  TABLES.forEach((t, i) => { put('table#' + i + ' x0', t.x0); put('table#' + i + ' x1', t.x1); });
  BENCH_BREAKS.forEach((b, i) => put('break#' + i, typeof b === 'number' ? b : b.x));
  PROPS.forEach(p => put('prop ' + p.kind + (p.study ? ' ' + p.study : ''), p.x));
  FILM_RELAYS.forEach(r => put('film ' + r.kind, r.x));
  (typeof LIGHT_GRID !== 'undefined' ? LIGHT_GRID : []).forEach((L, i) => put('lamp#' + i, L.x));
  (typeof PROJECTORS !== 'undefined' ? PROJECTORS : []).forEach((p, i) => put('projector#' + i, p.x));
  (typeof DESK_SCREENS !== 'undefined' ? DESK_SCREENS : []).forEach(d => put('desk ' + d.beat, d.x));
  (typeof TALL_UNITS !== 'undefined' ? TALL_UNITS : []).forEach((u, i) => put('tall#' + i, u.x));
  (typeof PLATES !== 'undefined' ? PLATES : []).forEach((p, i) => put('plate#' + i, p.x));
  SEGMENTS.forEach((s, i) => { put('era' + i + ' x0', s.x0); put('era' + i + ' x1', s.x1); });
  for (const n of ['REC_L','REC_R','REC3_L','REC3_R','REC93_L','REC93_R','REC2_L','REC2_R','REC18_L','REC18_R',
                   'REC4_L','REC4_R','REC23_L','REC23_R','REC17_L','REC17_R','FACT_X','FIN_X','WORLD_END','BOARD_X'])
    try { put(n, eval(n)); } catch(e){}
  // где врезка встаёт в мире без пробы
  let s = 0; for (const c of CUTS) if (c.on && !/^probe/.test(c.id || '') && c.at < ${+AT}) s += c.w;
  o.__cutX = ${+AT} + s;
  return JSON.stringify(o);
})()`;

async function load(q){
  const p = await page();
  await p.call('Page.enable'); await p.call('Runtime.enable');
  await p.call('Page.navigate', {url: `http://127.0.0.1:${PORT}/expo/expo.html?rq=1${q}&nc=${Date.now()}`});
  for (let i = 0; i < 40; i++){
    await sleep(500);
    const r = await p.call('Runtime.evaluate', {expression: 'typeof BEATS !== "undefined" && TABLES.length > 0 && typeof FILM_RELAYS !== "undefined" && FILM_RELAYS.length > 0', returnByValue: true});
    if (r.result && r.result.result && r.result.result.value) break;
  }
  await sleep(1500);
  const r = await p.call('Runtime.evaluate', {expression: DUMP, returnByValue: true});
  p.close();
  if (!r.result || r.result.exceptionDetails) throw new Error('dump failed: ' + JSON.stringify(r.result && r.result.exceptionDetails));
  return JSON.parse(r.result.result.value);
}

const a = await load('');
const b = await load(`&cut=${AT}:${WD}`);
const cx = a.__cutX, w = +WD;
const want = x => (x >= cx ? w : 0);
const out = [];
/* 1. ЖЁСТКИЕ ТОЧКИ ЗАЛА: бухты, финал, табло, эпохи — ровно на w справа, 0 слева */
for (const k of Object.keys(a).filter(k => /^[A-Z_0-9]+$|^era/.test(k) && k !== '__cutX')){
  const d = b[k] - a[k];
  if (Math.abs(d - want(a[k])) > 1) out.push(`  fixed point   ${String(Math.round(a[k])).padStart(6)}  moved ${Math.round(d)}, want ${want(a[k])}   ${k}`);
}
/* 2. ГОДЫ: порядок по годам не нарушен, и никто не уехал против врезки или
   дальше неё (внутри эпохи ритм вправе их раздвинуть — это не ошибка) */
const yr = k => parseInt(k.slice(5), 10);
const beatsB = Object.keys(b).filter(k => /^beat \d/.test(k) && !k.includes(' · ')).sort((p, q) => b[p] - b[q]);
for (let i = 1; i < beatsB.length; i++)
  if (yr(beatsB[i]) < yr(beatsB[i - 1])) out.push(`  ORDER         ${beatsB[i - 1]} (${Math.round(b[beatsB[i - 1]])}) stands left of ${beatsB[i]} (${Math.round(b[beatsB[i]])})`);
for (const k of Object.keys(a).filter(k => /^beat \d/.test(k) && !k.includes(' · '))){
  const d = b[k] - a[k];
  if (Math.sign(d) && Math.sign(d) !== Math.sign(w) || Math.abs(d) > Math.abs(w) + 1)
    out.push(`  beat          ${String(Math.round(a[k])).padStart(6)}  moved ${Math.round(d)} (cut ${w})   ${k}`);
}
/* 3. ВЕЩИ НА СТЕНЕ ДЕРЖАТСЯ СВОЕГО ГОДА: смещение от бита не меняется */
for (const k of Object.keys(a).filter(k => k.includes(' · '))){
  const beat = k.split(' · ')[0];
  const off = (a[k] - a[beat]) - (b[k] - b[beat]);
  if (Math.abs(off) > 1) out.push(`  attached      ${k} drifted ${Math.round(-off)} from its year`);
}
/* 4. ПРИЛАВКИ И РАЗРЫВЫ: каждый край должен найтись после пробы — на месте, на w
   или вместе с ближайшим годом */
const edges = o => Object.keys(o).filter(k => /^table#|^break#/.test(k)).map(k => o[k]);
const ea = edges(a), eb = edges(b);
const beatMove = x => { let best = null, bd = 1e9;
  for (const k of Object.keys(a)) if (/^beat \d/.test(k) && !k.includes(' · ') && k in b){ const d = Math.abs(a[k] - x); if (d < bd){ bd = d; best = b[k] - a[k]; } }
  return best || 0; };
for (const x of ea){
  const cands = [want(x), 0, w, beatMove(x)];
  if (!cands.some(d => eb.some(y => Math.abs(y - (x + d)) < 2)))
    out.push(`  counter edge  ${String(Math.round(x)).padStart(6)}  has no match after the cut (nearest: ${Math.round(eb.reduce((m, y) => Math.abs(y - x) < Math.abs(m - x) ? y : m, 1e9))})`);
}
if (ea.length !== eb.length) out.push(`  counters      ${ea.length / 1} edges before, ${eb.length} after`);
console.log(`cut ${AT}:${WD} lands at world ${Math.round(cx)}; ${Object.keys(a).length - 1} things checked`);
console.log(out.length ? out.length + ' problem(s):\n' + out.join('\n') : 'clean — everything follows the hall');
process.exit(out.length ? 1 : 0);
