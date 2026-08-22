# МУЗЫКА ЗАЛА — промпты для Suno (редакция 2)

Правка после первой партии: треки вышли **слишком лирическими**. Печаль сидит в
гармонии, обработкой её не вынуть, поэтому она убрана из самих промптов —
пентатоника и модальность вместо минорных разрешений, «спокойно и буднично»
вместо «меланхолично». Всё остальное прежнее: один ключ, один темп, лимит 500.

Каждый промпт самодостаточен — копируй целиком.

---

## 1 · WELCOME / ATTRACT → `mus_welcome.mp3`

<sub>477/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor pentatonic, modal and open — no sad or plaintive harmony, no lament, calm and matter-of-fact rather than emotional. Sparse quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. One sustained open fifth on a felt upright piano, almost the room itself, a low tungsten hum beneath; one cello note every eight bars. No melody, no rhythm. A workshop before anyone arrives. Tape warmth, vinyl noise floor.
```

---

## 2 · 1907–1979 · РЕМЕСЛО → `mus_era1.mp3`

<sub>481/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor pentatonic, modal and open — no sad or plaintive harmony, no lament, calm and matter-of-fact rather than emotional. Sparse quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. Felt upright piano and one cello in a small wooden room. The pulse is the work itself: a soft metronome tick, a faint hand-tool tap on a bench. Patient, warm, hand-made, unsentimental. 1950s tape, wow and flutter. No drum kit.
```

---

## 3 · 1979–1989 · МАСШТАБ ПО ПОЧТЕ → `mus_era2.mp3`

<sub>487/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor pentatonic, modal and open — no sad or plaintive harmony, no lament, calm and matter-of-fact rather than emotional. Sparse quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. Juno-style pad and soft Rhodes turning between two chords, a quiet shaker. Steady and quietly hopeful — a small lab finding it can reach the whole country by post. Tape wobble, cassette hiss, gentle chorus. No lead melody, no snare.
```

---

## 4 · 1989–2009 · ЦИФРА НА ВЕРСТАКЕ → `mus_era3.mp3`

<sub>476/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor pentatonic, modal and open — no sad or plaintive harmony, no lament, calm and matter-of-fact rather than emotional. Sparse quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. DX7-style FM bells, a slow four-note arpeggio on a soft digital pad, a very low dry drum-machine pulse, more felt than heard. A green CRT in a dim night laboratory: curiosity, not longing. Dusty, detuned, faint bit-crush.
```

---

## 5 · 2010–2026 · БЕЛЫЙ СВЕТ → `mus_era4.mp3`

<sub>470/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor pentatonic, modal and open — no sad or plaintive harmony, no lament, calm and matter-of-fact rather than emotional. Sparse quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. Glassy celeste and marimba interlocking over a wide granular pad that breathes slowly. Warm despite the precision, human, never clinical. A distant piano note now and then, long decay. Nothing percussive, no risers.
```

---

## 6 · ФИНАЛ 2026 → `mus_finale.mp3`

<sub>455/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor pentatonic, modal and open — no sad or plaintive harmony, no lament, calm and matter-of-fact rather than emotional. Sparse quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. The opening figure returns on celeste and soft glass synth over a warm pad, cello low underneath. Settled and clear — neither triumphant nor wistful. Long decay, generous space, ending where it began.
```

---

## Что делает `tools/audio_prep.py` с готовыми файлами

Первая партия уже прогнана — результат лежит рядом как `mus_*.m4a`:

- **вырезает у каждого трека самую характерную минуту.** Восемь спектральных
  полос, скользящее окно 60 с, выбирается участок, наименее похожий на средний
  профиль всех шести. Найденные точки: 52 с, 60 с, 106 с, 2 с, 110 с, 80 с —
  ровно то, о чём ты говорил: суть у каждого в своём месте;
- **делает бесшовную петлю** — хвост складывается с началом по равной мощности;
- **даёт каждой эпохе свою комнату:** ремесло теряет верх и получает дерево,
  почтовые годы — кассетное подвывание и шипение, первая цифра прорежена снизу
  и подсвечена в колокольном диапазоне, белая эпоха открыта вверх. Это и делает
  похожие треки разными на слух;
- **ровняет громкость** на −22 dB RMS, заведомо тише любой речи.

Перегенерируешь по новым промптам — просто положи файлы как `1.mp3`…`6.mp3` и
скажи, я прогоню заново одной командой.
