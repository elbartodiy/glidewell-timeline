# МУЗЫКА ЗАЛА — промпты для Suno

## Сквозные правила (почему они важны)

Все шесть треков живут в **одной тональности (A minor) и в одном темпе (68 BPM)**.
Это не педантизм: зал — непрерывное пространство, эпохи переходят одна в другую
на ходу камеры, и движок будет делать кроссфейд. Разные тональности на стыке
дадут фальшь, разные темпы — спотыкание. Один ключ и один пульс означают, что
любые два трека можно наложить в любой момент, и это будет звучать как одна
композиция, меняющая инструмент.

**Технический блок — добавлять в КАЖДЫЙ промпт (Style / Prompt):**

```
Instrumental only, no vocals, no lyrics, no choir. 68 BPM, key A minor.
Extremely sparse and quiet — background music for a museum room that must never
compete with a speaking voice. No builds, no drops, no crescendos, no drum
fills, no cinematic hits: steady dynamics from the first bar to the last.
Loopable — start and end on the same sustained chord, no fade in, no fade out,
no silence at either end. Warm, wide, patient.
```

**Exclude styles (если Suno спросит):**
`vocals, singing, choir, EDM, dubstep, trap, big orchestral swells, trailer
percussion, hip-hop drums, aggressive bass`

Длительность: 2–3 минуты хватит, движок зациклит.

---

## 1. WELCOME / ATTRACT — «до начала времени»
Стартовый кадр: логотип под потолком, натюрморт под лампой, зал ждёт.
Музыки почти нет — только воздух комнаты и одно дыхание аккорда.

```
A single sustained minor chord on a felt-muted upright piano, so quiet it is
almost the room itself. Underneath: the low hum of an old tungsten lamp and
faint air. One cello note enters every eight bars and decays. Nothing else —
no melody yet, no rhythm at all. The sound of a workshop before anyone arrives.
Analog tape warmth, gentle vinyl noise floor.
```

---

## 2. ЭПОХА 1 · 1907–1979 — РЕМЕСЛО
Дерево, вольфрам, руки. Пульс здесь — не барабан, а сама работа.

```
Slow chamber miniature for felt upright piano and one solo cello, recorded in a
small wooden room. The pulse is not a drum kit but the work itself: a soft
metronome tick and the occasional faint tap of a hand tool on a bench, low in
the mix, like a clock in another room. Warm tungsten-lit melancholy, patient and
unhurried, the dignity of a craft done by hand. 1950s tape recording, wow and
flutter, brushed felt hammers, no reverb tail longer than the room.
```

---

## 3. ЭПОХА 2 · 1979–1989 — МАСШТАБ ПО ПОЧТЕ
Девять лабораторий сходятся в одну, кейсы едут по стране. Тепло, но уже машина.

```
Warm analog optimism at walking pace: a Juno-style polysynth pad, a soft Rhodes
electric piano playing two alternating chords, a quiet shaker keeping time.
Hopeful but restrained — the sound of a small operation discovering it can reach
the whole country by post. Slight tape wobble, cassette hiss, gentle chorus on
the Rhodes. No lead melody, no snare, nothing bright or brassy.
```

---

## 4. ЭПОХА 3 · 1989–2009 — ЦИФРА ПРИХОДИТ НА ВЕРСТАК
Зелёные CRT, серые панели, первые сканы. Прохладнее, любопытнее.

```
Early-digital ambience, cool and curious: FM bell tones in the style of a DX7,
a slow four-note arpeggio on a soft digital pad, and a very low, very dry drum
machine pulse — barely audible, more felt than heard. The feeling of a green CRT
glowing in a dim laboratory at night; wonder without excitement. Dusty, slightly
detuned, faint bit-crush on the bells. No bass drops, no acid lines, no vocals.
```

---

## 5. ЭПОХА 4 · 2010–2026 — БЕЛЫЙ СВЕТ, МАШИНЫ, ТОЧНОСТЬ
Белый камень, роботы, ИИ. Чисто и тепло одновременно — иначе выйдет холодная реклама.

```
Clean minimal ambient: glassy celeste and marimba figures repeating in gentle
interlocking patterns, over a wide granular pad that breathes very slowly. Warm
despite the precision — the room is white and bright, but the music must stay
human. Occasional single piano note, far away, with long decay. Nothing
percussive, nothing clinical, no synth arpeggios racing, no risers.
```

---

## 6. ФИНАЛ · 2026 — ЗАМЫКАНИЕ ДУГИ
Композиционная идея: **та же мелодия, что во welcome, но сыгранная палитрой
последней эпохи.** Век прошёл — тема осталась, сменился инструмент. Это самый
дешёвый и самый сильный способ дать зрителю почувствовать замкнувшийся круг.

```
The same simple minor motif as the opening piece, but now played on celeste and
soft glass-like synth over a wide warm pad, with the cello returning underneath
in its lowest register. Resolved and quiet, not triumphant — an arc closing, not
a fanfare. Long decay, generous space, the last chord held and unresolved enough
to begin again.
```

**Как получить именно ту же мелодию:** сгенери сначала welcome (п.1), затем в
Suno сделай на него **Cover** с промптом финала — тема сохранится, палитра
сменится. Если Cover даст не то, просто пришли welcome-трек: движок может сам
использовать его в финале с другим микшированием.

---

## Что мне нужно от тебя

Готовые файлы в `expo/audio/` с такими именами (mp3, 128–192 kbps достаточно):

| Файл | Где играет |
|---|---|
| `mus_welcome.mp3` | стартовый кадр и attract-режим |
| `mus_era1.mp3` | 1907–1979 |
| `mus_era2.mp3` | 1979–1989 |
| `mus_era3.mp3` | 1989–2009 |
| `mus_era4.mp3` | 2010–2026 |
| `mus_finale.mp3` | финальный натюрморт |

## Что сделаю я

- Кроссфейд между эпохами по положению камеры, а не по щелчку: трек эпохи
  подмешивается по мере входа в неё, длина перехода — примерно ширина порога
  рекреации, так что смена материала зала и смена звука совпадут.
- **Дакинг:** когда играет речь спикера или плёнка проектора, музыка уходит
  вниз на 12–14 dB и возвращается после. Иначе музыка съест голос.
- Общая громкость тихая по умолчанию, с одной точкой настройки.
- Автозапуск по первому касанию (браузеры не дают звук до жеста) и пауза, когда
  киоск уходит в простой без зрителя.
