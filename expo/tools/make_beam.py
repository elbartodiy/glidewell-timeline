#!/usr/bin/env python3
"""Луч прожектора — PNG-текстура для тумбы 1989-го (Эльдар, 27.10.2026: «лучи
поменять на сгенерированные полупрозрачные пнг»).

Белый луч в альфе: вершина (линза) — середина верхнего края, подошва — нижний
край. Вдоль луча яркость РОВНАЯ: где луч горит сильнее (на экспонате) и где
гаснет, задаёт код (drawBeamImg), он же красит в цвет beamRGB. В текстуре —
только то, чего градиент не умеет: мягкая кромка, полосы от линзы и дымка в
воздухе (пылинки сняты 27.10.2026).

    python3 expo/tools/make_beam.py      # → assets/photo/beam89_{a,b}.png + .webp
"""
import os
import numpy as np
from PIL import Image, ImageFilter

W, H = 384, 1536
CORE = 1 / 1.7            # кромка ядра в долях полуширины листа у подошвы (как самый широкий проход softBeam)
HEAD = 0.30               # ширина у линзы относительно подошвы
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets', 'photo')


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def fbm(rng, octaves, sx, sy):
    """дымка: шум из нескольких октав, вытянутый вдоль луча"""
    acc = np.zeros((H, W)); amp = 1.0; tot = 0
    for o in range(octaves):
        gw, gh = max(2, int(sx * 2 ** o)), max(2, int(sy * 2 ** o))
        g = rng.random((gh, gw)).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        acc += amp * (np.asarray(im, np.float32) / 255 - 0.5); tot += amp; amp *= 0.55
    return acc / tot


def make(seed):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    v = (y + 0.5) / H                                  # 0 у линзы, 1 у подошвы
    xs = (x + 0.5) / W * 2 - 1                         # −1…1 поперёк листа
    hw = CORE * (HEAD + (1 - HEAD) * v)                # полуширина ядра в этой строке
    u = np.abs(xs) / hw                                # 0 ось, 1 кромка ядра
    a_ang = xs / hw                                    # «угол» от линзы: полосы расходятся веером

    core = 1 - smooth(0.55, 1.2, u)                    # мягкая кромка
    hot = np.exp(-(u / 0.42) ** 2)                     # горячая ось
    halo = np.exp(-(u / 1.55) ** 2)                    # рассеянный свет вокруг
    base = 0.62 * core + 0.20 * hot + 0.18 * halo

    # полосы от линзы: сумма синусов по «углу», чуть плывут вдоль луча
    streak = np.zeros_like(xs)
    for f in rng.uniform(2.5, 16, 9):
        ph = rng.uniform(0, 2 * np.pi); drift = rng.uniform(-0.6, 0.6)
        streak += np.sin(a_ang * f + ph + drift * v * 3) / 9
    streak = 1 + 0.55 * streak                         # ±~15 %

    smoke = 1 + 0.28 * fbm(rng, 4, 3, 10)              # дымка — длинные пряди вдоль луча
    alpha = base * streak * smoke

    # пылинок нет (Эльдар, 27.10.2026: «чтобы там не было точек пыли — они
    # статичные, плохо смотрятся — только лучи»); было 340 точек внутри ядра

    alpha *= 1 - smooth(0.82, 1.0, np.abs(xs))          # к краю листа — в ноль, без ступеньки
    alpha = np.clip(alpha / 0.95, 0, 1) ** 1.05
    A = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    white = Image.new('L', (W, H), 255)
    return Image.merge('RGBA', (white, white, white, A))


for name, seed in (('a', 1989), ('b', 1993)):
    im = make(seed)
    p = os.path.join(OUT, f'beam89_{name}.png')   # новое имя — чтобы киоск не держал из кэша лист с пылинками
    im.save(p, optimize=True)
    im.save(p[:-4] + '.webp', lossless=True, quality=100)
    print(p, os.path.getsize(p) // 1024, 'KB')
