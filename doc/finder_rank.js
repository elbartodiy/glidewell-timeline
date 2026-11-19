/* Finder: ranking by words. One file for the page (doc/interviews.html) and the local server (finder_server.mjs).
   Eldar's rule 2026-11-18: no quotes. A query of several words is a phrase by default:
     0 the phrase word for word → 1 the same phrase in other word forms → 2 all the words, apart (closer = higher)
     → 3 some of the words. Fragments with none of the words never get here; meaning finds them in its own block.
   Search is English only (transcripts are English; Russian is for reading). */
(function (G) {
  'use strict';
  var STOP = new Set('the a an and or of to in on is it that this was were be are for with as at by from i you he she we they his her my our your what where when how did do does about there here so but not no yes'.split(' '));

  // ---- Porter stemmer (M.F. Porter, 1980) ----
  var step2list = { ational: 'ate', tional: 'tion', enci: 'ence', anci: 'ance', izer: 'ize', bli: 'ble', alli: 'al', entli: 'ent', eli: 'e', ousli: 'ous',
    ization: 'ize', ation: 'ate', ator: 'ate', alism: 'al', iveness: 'ive', fulness: 'ful', ousness: 'ous', aliti: 'al', iviti: 'ive', biliti: 'ble', logi: 'log' };
  var step3list = { icate: 'ic', ative: '', alize: 'al', iciti: 'ic', ical: 'ic', ful: '', ness: '' };
  var c = '[^aeiou]', v = '[aeiouy]', C = c + '[^aeiouy]*', V = v + '[aeiou]*';
  var mgr0 = new RegExp('^(' + C + ')?' + V + C), meq1 = new RegExp('^(' + C + ')?' + V + C + '(' + V + ')?$'),
      mgr1 = new RegExp('^(' + C + ')?' + V + C + V + C), s_v = new RegExp('^(' + C + ')?' + v);
  function porter(w) {
    var stem, suffix, re, re2, re3, re4, fp, first;
    if (w.length < 3) return w;
    first = w.charAt(0); if (first === 'y') w = 'Y' + w.slice(1);
    re = /^(.+?)(ss|i)es$/; re2 = /^(.+?)([^s])s$/;
    if (re.test(w)) w = w.replace(re, '$1$2'); else if (re2.test(w)) w = w.replace(re2, '$1$2');
    re = /^(.+?)eed$/; re2 = /^(.+?)(ed|ing)$/;
    if (re.test(w)) { fp = re.exec(w); if (mgr0.test(fp[1])) w = w.slice(0, -1); }
    else if (re2.test(w)) { fp = re2.exec(w); stem = fp[1];
      if (s_v.test(stem)) { w = stem; re2 = /(at|bl|iz)$/; re3 = /([^aeiouylsz])\1$/; re4 = new RegExp('^' + C + v + '[^aeiouwxy]$');
        if (re2.test(w)) w += 'e'; else if (re3.test(w)) w = w.slice(0, -1); else if (re4.test(w)) w += 'e'; } }
    re = /^(.+?)y$/; if (re.test(w)) { fp = re.exec(w); stem = fp[1]; if (s_v.test(stem)) w = stem + 'i'; }
    re = /^(.+?)(ational|tional|enci|anci|izer|bli|alli|entli|eli|ousli|ization|ation|ator|alism|iveness|fulness|ousness|aliti|iviti|biliti|logi)$/;
    if (re.test(w)) { fp = re.exec(w); stem = fp[1]; suffix = fp[2]; if (mgr0.test(stem)) w = stem + step2list[suffix]; }
    re = /^(.+?)(icate|ative|alize|iciti|ical|ful|ness)$/;
    if (re.test(w)) { fp = re.exec(w); stem = fp[1]; suffix = fp[2]; if (mgr0.test(stem)) w = stem + step3list[suffix]; }
    re = /^(.+?)(al|ance|ence|er|ic|able|ible|ant|ement|ment|ent|ou|ism|ate|iti|ous|ive|ize)$/; re2 = /^(.+?)(s|t)(ion)$/;
    if (re.test(w)) { fp = re.exec(w); stem = fp[1]; if (mgr1.test(stem)) w = stem; }
    else if (re2.test(w)) { fp = re2.exec(w); stem = fp[1] + fp[2]; if (mgr1.test(stem)) w = stem; }
    re = /^(.+?)e$/;
    if (re.test(w)) { fp = re.exec(w); stem = fp[1]; re2 = new RegExp('^' + C + v + '[^aeiouwxy]$');
      if (mgr1.test(stem) || (meq1.test(stem) && !re2.test(stem))) w = stem; }
    re = /ll$/; if (re.test(w) && mgr1.test(w)) w = w.slice(0, -1);
    if (first === 'y') w = 'y' + w.slice(1);
    return w;
  }
  var cache = new Map();
  function stem(w) {
    var s = cache.get(w); if (s !== undefined) return s;
    var x = w.replace(/'s$/, '').replace(/'/g, '');
    s = /^[a-z]+$/.test(x) ? porter(x) : x;   // numbers, names with digits, other alphabets: as they are
    if (cache.size < 200000) cache.set(w, s); return s;
  }

  // words: letters/digits/apostrophes; hyphens and punctuation split ("all-ceramic" = "all ceramic")
  var WORD = /[\p{L}\p{N}]+(?:['’][\p{L}]+)*/gu;
  function lower(t) { return t.toLowerCase().replace(/ё/g, 'е').replace(/’/g, "'"); }
  function words(text) { return (String(text || '').match(WORD) || []).map(lower); }
  function prep(text) { var w = words(text), s = w.map(stem); return { w: w, s: s, set: new Set(s) }; }

  var STOP_ST = null;             // stop words as stems ("was" → "wa"): df skips them the same way query() does
  function stats(docs) {          // docs: array of prep() results (or null)
    if (!STOP_ST) { STOP_ST = new Set(); STOP.forEach(function (w) { STOP_ST.add(stem(w)); }); }
    var df = new Map(), sum = 0, n = 0;
    docs.forEach(function (d) { if (!d) return; n++; sum += d.s.length; d.set.forEach(function (x) { if (!STOP_ST.has(x)) df.set(x, (df.get(x) || 0) + 1); }); });
    return { df: df, N: n || 1, avg: sum / (n || 1) || 1 };
  }
  function query(q) {
    var qw = words(q), qs = qw.map(stem), cs = [];
    qs.forEach(function (x, k) { if (!STOP.has(qw[k]) && cs.indexOf(x) < 0) cs.push(x); });
    if (!cs.length) qs.forEach(function (x) { if (cs.indexOf(x) < 0) cs.push(x); });   // "in the": all words count
    // phrase: several words; oneWord: a phrase around one meaningful word ("in the lab") — tier 2 is then just that word
    return { qw: qw, qs: qs, cs: cs, phrase: qw.length > 1, oneWord: qw.length > 1 && cs.length === 1 };
  }
  function seq(arr, pat) {         // how many times pat stands in arr word for word
    var n = 0, L = pat.length;
    outer: for (var i = 0; i + L <= arr.length; i++) { for (var j = 0; j < L; j++) if (arr[i + j] !== pat[j]) continue outer; n++; }
    return n;
  }
  function windowSpan(s, cs) {     // the shortest stretch of words that holds every query word
    var pos = [], need = cs.length, cnt = new Map(), have = 0, best = Infinity, l = 0;
    s.forEach(function (x, i) { if (cs.indexOf(x) > -1) pos.push([i, x]); });
    for (var r = 0; r < pos.length; r++) {
      var x = pos[r][1]; cnt.set(x, (cnt.get(x) || 0) + 1); if (cnt.get(x) === 1) have++;
      while (have === need) { best = Math.min(best, pos[r][0] - pos[l][0] + 1);
        var y = pos[l][1]; cnt.set(y, cnt.get(y) - 1); if (!cnt.get(y)) have--; l++; }
    }
    return best;
  }
  function bm25(d, cs, st) {
    var s = 0, len = d.s.length;
    cs.forEach(function (x) { if (!d.set.has(x)) return; var f = 0; d.s.forEach(function (y) { if (y === x) f++; });
      var n = st.df.get(x) || 0; s += Math.log(1 + (st.N - n + .5) / (n + .5)) * f * 2.2 / (f + 1.2 * (.25 + .75 * len / st.avg)); });
    return s;
  }

  /* rank(Q, docs, pool, st, sem)
     docs[i] = prep(text); pool = indices allowed; sem = optional array of meaning scores by index (orders tier 3).
     → { hits: [{i, tier, m}], none: [indices with none of the words], counts: [n0,n1,n2,n3] } */
  function rank(Q, docs, pool, st, sem) {
    var tiers = [[], [], [], []], none = [], cs = Q.cs;
    pool.forEach(function (i) {
      var d = docs[i]; if (!d) return; var m = 0;
      for (var k = 0; k < cs.length; k++) if (d.set.has(cs[k])) m++;
      if (!m) { none.push(i); return; }
      var b = bm25(d, cs, st), all = m === cs.length, n;
      if (all && (n = seq(d.w, Q.qw))) tiers[0].push({ i: i, tier: 0, m: m, k: [n > 1 ? 1 : 0, b] });
      else if (all && (n = seq(d.s, Q.qs))) tiers[1].push({ i: i, tier: 1, m: m, k: [n > 1 ? 1 : 0, b] });
      else if (all) tiers[2].push({ i: i, tier: 2, m: m, k: [-windowSpan(d.s, cs), b] });
      else tiers[3].push({ i: i, tier: 3, m: m, b: b });
    });
    var byK = function (a, z) { return z.k[0] - a.k[0] || z.k[1] - a.k[1]; };
    tiers[0].sort(byK); tiers[1].sort(byK); tiers[2].sort(byK);
    // some of the words: more of the query words first; inside that, words (BM25) and meaning fused by rank (RRF)
    var t3 = tiers[3];
    if (sem) {
      var rb = new Map(), rs = new Map();
      t3.slice().sort(function (a, z) { return z.b - a.b; }).forEach(function (x, n) { rb.set(x.i, n); });
      t3.slice().sort(function (a, z) { return sem[z.i] - sem[a.i]; }).forEach(function (x, n) { rs.set(x.i, n); });
      t3.forEach(function (x) { x.f = 1 / (60 + rb.get(x.i)) + 1 / (60 + rs.get(x.i)); });
      t3.sort(function (a, z) { return z.m - a.m || z.f - a.f; });
    } else t3.sort(function (a, z) { return z.m - a.m || z.b - a.b; });
    return { hits: tiers[0].concat(tiers[1], tiers[2], t3), none: none, counts: tiers.map(function (t) { return t.length; }) };
  }

  /* spans(text, Q, tier) → [[start,end],…] to mark: the phrase as one piece (tiers 0–1), otherwise each query word */
  function spans(text, Q) {
    var t = String(text || ''), toks = [], m; WORD.lastIndex = 0;
    while ((m = WORD.exec(t))) { var w = lower(m[0]); toks.push({ a: m.index, b: m.index + m[0].length, s: stem(w) }); }
    var out = [], L = Q.qs.length, used = new Array(toks.length);
    if (L > 1) for (var i = 0; i + L <= toks.length; i++) {
      var ok = true; for (var j = 0; j < L; j++) if (toks[i + j].s !== Q.qs[j]) { ok = false; break; }
      if (ok) { out.push([toks[i].a, toks[i + L - 1].b]); for (j = 0; j < L; j++) used[i + j] = 1; i += L - 1; }
    }
    toks.forEach(function (x, k) { if (!used[k] && Q.cs.indexOf(x.s) > -1) out.push([x.a, x.b]); });
    return out.sort(function (a, z) { return a[0] - z[0]; });
  }

  /* who(q, known) → {p, rest} when the query names an interviewee: that person becomes the filter.
     Whole words only: a surname, or a first name that is not an ordinary English word ("theme park" is not Dr. Park).
     The page shows the filter with "Search everyone" to undo it. */
  var PEOPLE = { 'Sergei Azernikov': [['azernikov'], ['sergei']], 'Dr. Howard Farran': [['farran'], ['howard']], 'Dr. Paul Feuerstein': [['feuerstein'], ['paul']],
    'Dr. Marie Buell': [['buell'], ['marie']], 'Dr. Paresh Patel': [['patel'], ['paresh']], 'Dr. Randy Resnik': [['resnik'], ['randy']],
    'Dr. Neil Park': [['neil', 'park'], ['dr', 'park'], ['doctor', 'park'], ['neil']], 'Dr. Abdul Alas': [['abdul']], 'Edsel Labao': [['labao'], ['edsel']] };
  function who(q, known) {
    var w = words(q).map(function (x) { return x.replace(/'s$/, ''); });
    for (var p in PEOPLE) { if (known && !known[p]) continue;
      for (var k = 0; k < PEOPLE[p].length; k++) { var pat = PEOPLE[p][k];
        for (var i = 0; i + pat.length <= w.length; i++) {
          var ok = true; for (var j = 0; j < pat.length; j++) if (w[i + j] !== pat[j]) { ok = false; break; }
          if (!ok) continue;
          var a = i, b = i + pat.length; if (a > 0 && (w[a - 1] === 'dr' || w[a - 1] === 'doctor')) a--;
          return { p: p, rest: w.slice(0, a).concat(w.slice(b)).join(' ') };
        } } }
    return null;
  }

  G.FinderRank = { who: who, PEOPLE: PEOPLE, STOP: STOP, stem: stem, words: words, prep: prep, stats: stats, query: query, rank: rank, spans: spans };
})(typeof window !== 'undefined' ? window : globalThis);
