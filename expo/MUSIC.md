# МУЗЫКА ЗАЛА — промпты для Suno

Шесть промптов, **каждый самодостаточен и уложен в лимит 500 знаков** — копируй
целиком, ничего добавлять не надо. Все в одной тональности (A minor) и темпе
(68 BPM): зал непрерывный, эпохи сменяются на ходу камеры, движок сводит их
кроссфейдом — при разных тональностях стык фальшивит, при разных темпах
спотыкается. Один ключ и один пульс = любые два трека накладываются в любой
момент и звучат как одна композиция, сменившая инструмент.

Длительность 2–3 минуты, движок зациклит. Файлы кидай в `expo/audio/`.

---

## 1 · WELCOME / ATTRACT → `mus_welcome.mp3`

<sub>401/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor. Sparse, quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. One sustained minor chord on a felt-muted upright piano, almost the room itself; a low tungsten hum and faint air beneath; one cello note every eight bars, decaying. No melody, no rhythm. A workshop before anyone arrives. Analog tape warmth, vinyl noise floor.
```

---

## 2 · 1907–1979 · РЕМЕСЛО → `mus_era1.mp3`

<sub>416/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor. Sparse, quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. Slow chamber miniature: felt upright piano and one cello in a small wooden room. The pulse is the work itself — a soft metronome tick and a faint hand-tool tap on a bench, low in the mix. Warm tungsten melancholy, patient, hand-made. 1950s tape, wow and flutter. No drum kit.
```

---

## 3 · 1979–1989 · МАСШТАБ ПО ПОЧТЕ → `mus_era2.mp3`

<sub>414/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor. Sparse, quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. Warm analog optimism at walking pace: Juno-style polysynth pad, soft Rhodes turning between two chords, a quiet shaker. Hopeful but restrained — a small lab finding it can reach the whole country by post. Tape wobble, cassette hiss, gentle chorus. No lead melody, no snare.
```

---

## 4 · 1989–2009 · ЦИФРА НА ВЕРСТАКЕ → `mus_era3.mp3`

<sub>415/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor. Sparse, quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. Early-digital ambience, cool and curious: DX7-style FM bells, a slow four-note arpeggio on a soft digital pad, a very low dry drum-machine pulse, more felt than heard. A green CRT glowing in a dim night laboratory; wonder without excitement. Dusty, detuned, faint bit-crush.
```

---

## 5 · 2010–2026 · БЕЛЫЙ СВЕТ → `mus_era4.mp3`

<sub>409/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor. Sparse, quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. Clean minimal ambient: glassy celeste and marimba interlocking gently over a wide granular pad that breathes slowly. Warm despite the precision — white and bright, but human, never clinical. A distant piano note now and then, long decay. Nothing percussive, no risers.
```

---

## 6 · ФИНАЛ 2026 → `mus_finale.mp3`

<sub>420/500 знаков</sub>

```
Instrumental, no vocals. 68 BPM, A minor. Sparse, quiet museum background: steady dynamics, no builds or drops, loopable, no fade in or out. The opening motif returns, now on celeste and soft glass synth over a wide warm pad, cello underneath in its lowest register. Resolved and quiet, not triumphant — an arc closing, not a fanfare. Long decay, generous space, a final chord held just unresolved enough to begin again.
```

---

## Что сделаю я, когда файлы появятся

- Кроссфейд между эпохами по положению камеры, длиной примерно в порог рекреации —
  смена материала зала и смена звука совпадут.
- **Дакинг:** речь спикера или плёнка проектора опускают музыку на 12–14 dB.
- Тихо по умолчанию, одна точка настройки громкости.
- Автозапуск по первому касанию (браузеры не дают звук раньше) и пауза на простое.
