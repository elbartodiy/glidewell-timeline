#!/usr/bin/env python3
"""Cut the founding bench's two corners out of Eldar's render.

The counter of the founding bay is a PHOTOGRAPH (plate_bay_front.png, laid by
drawPlateBench and extended sideways by tiling two clean strips of itself), so
it had no ends: a run simply stopped on a straight cut. Eldar rendered the ends
for it — Artefacts/Interior/1sttablecorners.png, a short piece of the same
counter with both of its mitred corners — and this takes the two corners off it.

NOTHING IS REDRAWN. The corner is the render's own: the cut column is where the
mitre's diagonal reaches the back edge (read off the alpha), plus a margin of
plain counter for the join to dissolve into.

    python3 qa/cut_corners.py

The printed rows go into PL_END in expo.html.
"""
import numpy as np
from PIL import Image

ROOT = __file__.rsplit('/', 2)[0]   # .../expo — the renders and the cut-outs both live under it
SRC = f'{ROOT}/Artefacts/Interior/1sttablecorners.png'
OUT = f'{ROOT}/assets/photo'
JOIN = 90          # columns of plain counter kept past the mitre, for the dissolve


def rows(a):
    """the two rows the hall hangs this render by: the lit front arris (where the
    top surface ends) and the bottom of the bullnose (where the front begins)."""
    mid = a[:, int(a.shape[1] * .43):int(a.shape[1] * .57), :3].mean(axis=2).mean(axis=1)
    lo, hi = 20, int(a.shape[0] * .45)
    arris = lo + int(np.argmax(mid[lo:hi]))                 # the bright line along the front
    r = arris + 1
    while r < hi and mid[r] > 60: r += 1                    # down through the bullnose
    return arris, r                                          # (72, 94) on the file as delivered


def mitre_end(alpha, from_left):
    """the column where the mitre's diagonal reaches the render's back edge — the
    corner return is everything outside it."""
    n = alpha.shape[1]
    cols = range(n) if from_left else range(n - 1, -1, -1)
    for x in cols:
        col = np.nonzero(alpha[:, x] > 128)[0]
        if len(col) and col[0] <= 2:                        # the top surface is full depth here
            return x
    return 0 if from_left else n - 1


def cut():
    im = Image.open(SRC).convert('RGBA')
    a = np.asarray(im).astype(float)
    H, W = a.shape[0], a.shape[1]
    arris, bull = rows(a)
    lx = mitre_end(a[..., 3], True)
    rx = mitre_end(a[..., 3], False)
    l1 = min(W, lx + JOIN)
    r0 = max(0, rx - JOIN)
    im.crop((0, 0, l1, H)).save(f'{OUT}/bench_p1_left.png', optimize=True)
    im.crop((0, 0, l1, H)).save(f'{OUT}/bench_p1_left.webp', quality=95, method=6)
    im.crop((r0, 0, W, H)).save(f'{OUT}/bench_p1_right.png', optimize=True)
    im.crop((r0, 0, W, H)).save(f'{OUT}/bench_p1_right.webp', quality=95, method=6)
    print(f'{W}x{H}  arris row {arris}, bullnose ends {bull} ({bull - arris} rows thick)')
    print(f'   mitre closes at {lx} on the left and {rx} on the right')
    print(f'   left  0..{l1}  ({l1} cols)   right {r0}..{W}  ({W - r0} cols)')
    print(f"   PL_END = {{arris: {arris}, bull: {bull}, joinL: {l1 - lx}, joinR: {rx - r0}}}")


cut()
