#!/usr/bin/env node
/* ПРОВЕРКИ, КОТОРЫЕ МАШИНА МОЖЕТ СДЕЛАТЬ ЗА НАС.
 *
 * Каждое правило здесь — это ошибка, которая уже случилась и стоила Эльдару
 * круга: он увидел дефект, написал, я чинил. Смысл не в «линтере вообще», а в
 * том, чтобы одна и та же ошибка не приходила дважды. Если правило нельзя
 * проверить честно — его здесь нет: ложная тревога хуже отсутствия проверки.
 *
 *   node qa/lint.mjs            — проверить зал
 *   node qa/lint.mjs --list     — показать, что вообще проверяется
 *
 * Возвращает 1, если что-то найдено.
 */
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const FILE = join(HERE, '..', 'expo.html');
const src  = readFileSync(FILE, 'utf8');
const line = i => src.slice(0, i).split('\n').length;

const found = [];
const hit = (rule, i, what, why) => found.push({rule, ln: line(i), what, why});

/* ── R1 · КЕГЛЬ ОТ РАЗМЕРА КОРОБКИ, НЕ СВЕРЕННЫЙ С НЕЙ ───────────────────
   «UNITED STATES PATENT» вылезал за края листа, потому что и кегль, и
   разрядка были заданы долями ширины листа на глаз (Эльдар, 2026-09-23).
   Доля ширины — это догадка; ширина строки известна только измерению.
   Ищем: ctx.font, в котором размер выражен через переменную коробки
   (w/h/bw/bh/iw), а рядом рисуется текст и нигде не вызван measureText. */
{
  const re = /\bctx\.font\s*=\s*`[^`]*\$\{\s*\(?\s*(?:w|h|bw|bh|iw|sw)\s*\*/g;
  let m;
  while ((m = re.exec(src))){
    const win = src.slice(m.index, m.index + 900);
    if (!/fillText|strokeText/.test(win)) continue;
    if (/measureText/.test(win)) continue;
    hit('R1', m.index, 'кегль задан долей размера коробки',
        'строка может не влезть — измерь measureText и ужми, ПОСЛЕ того как выставлена разрядка');
  }
}

/* R2 снято. Оно было написано под реальную ошибку — монитор CAD печатал две
   фразы в одну точку, — но те два fillText стояли в РАЗНЫХ функциях
   (screenRead и drawScreenCAD), так что правило «два вызова с одинаковым y
   внутри одной функции» её бы не поймало, зато ловило дюжину честных
   двухколоночных строк. Правило, которое шумит и не ловит то, ради чего
   написано, — вред. Проверка осталась в чек-листе глазами.

   Вместо него — две проверки, которые не врут никогда: существование файлов,
   на которые зал ссылается. Пропавший клип или спрайт молча оставляет дыру,
   и заметить её можно только случайно. */

/* ── R2 · КЛИП, КОТОРОГО НЕТ НА ДИСКЕ ────────────────────────────────────── */
{
  const re = /src:\s*'(media\/[^']+)'/g;
  const seen = new Set();
  let m;
  while ((m = re.exec(src))){
    if (seen.has(m[1])) continue;
    seen.add(m[1]);
    if (!existsSync(join(HERE, '..', m[1])))
      hit('R2', m.index, `нет файла ${m[1]}`, 'страница сошлётся в пустоту — клип не откроется');
  }
}

/* ── R3 · ПРЕДМЕТ НА ПОСТАМЕНТЕ БЕЗ СПРАЙТА ──────────────────────────────── */
{
  const made = new Set([...src.matchAll(/PED_SPRITES\.([A-Za-z0-9_$]+)\s*=/g)].map(m => m[1]));
  const re = /ped:\s*\{[^}]*obj:\s*'([^']+)'/g;
  let m;
  while ((m = re.exec(src))){
    if (!made.has(m[1]))
      hit('R3', m.index, `ped obj:'${m[1]}' — такого спрайта не собирают`,
          'постамент будет пустым: добавь PED_SPRITES.' + m[1]);
  }
}

/* ── R4 · КАРТИНКА, ВШИТАЯ В СТРАНИЦУ ────────────────────────────────────
   2.43 МБ base64 внутри файла с 457 версиями — это 1.33 ГБ в истории.
   Картинки живут файлами в assets/, страница ссылается на них. */
{
  const re = /data:image\/[a-zA-Z0-9.+-]+;base64,[A-Za-z0-9+/=]{200,}/g;
  let m, n = 0;
  while ((m = re.exec(src))){ n++; if (n === 1) hit('R4', m.index, 'картинка вшита в страницу как base64',
      `таких ${'?'}: каждая версия файла весит на её размер — положи файлом в assets/ и сошлись`); }
  if (n > 1) found[found.length - 1].what += ` (всего ${n})`;
}

/* R5 (толщина линии без SS) снято: внутри ctx.scale(...) голое число — это
   правильно, а отличить одно от другого разбором текста нельзя. */

function splitArgs(s){
  const out = []; let d = 0, cur = '', q = null;
  for (const ch of s){
    if (q){ cur += ch; if (ch === q) q = null; continue; }
    if (ch === '"' || ch === "'" || ch === '`'){ q = ch; cur += ch; continue; }
    if ('([{'.includes(ch)) d++;
    if (')]}'.includes(ch)) d--;
    if (ch === ',' && d === 0){ out.push(cur); cur = ''; continue; }
    cur += ch;
  }
  out.push(cur);
  return out;
}

const RULES = {
  R1: 'кегль, заданный долей размера коробки, не сверенный измерением',
  R2: 'клип, которого нет на диске',
  R3: 'предмет на постаменте без спрайта',
  R4: 'картинка, вшитая в страницу как base64',
};

if (process.argv.includes('--list')){
  for (const [k, v] of Object.entries(RULES)) console.log(k + ' · ' + v);
  process.exit(0);
}

if (!found.length){
  console.log('lint: чисто (' + Object.keys(RULES).length + ' правил)');
  process.exit(0);
}
const by = {};
for (const f of found) (by[f.rule] ||= []).push(f);
for (const [rule, list] of Object.entries(by)){
  console.log(`\n${rule} · ${RULES[rule]} — ${list.length}`);
  for (const f of list.slice(0, 12)) console.log(`   expo.html:${f.ln}  ${f.what}\n      → ${f.why}`);
  if (list.length > 12) console.log(`   … и ещё ${list.length - 12}`);
}
console.log(`\nвсего: ${found.length}`);
process.exit(1);
