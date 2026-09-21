#!/usr/bin/env python3
"""Cut a counter render into the three pieces the hall lays it from.

Eldar's rule: a counter is an end return, ONE door repeated, and the other end
return. This takes his render of a whole counter and produces exactly that,
doing the four things that have each cost a round trip:

  * reads the file as RGBA and takes the bounding box from the ALPHA — the
    renders are transparent PNGs, and flattening them to RGB bakes the studio
    ground in and stands it behind the furniture;
  * straightens the worktop's back edge — the renders keep a little perspective
    at their ends, and a slanted end against a flat middle steps at the joint;
  * finds the door pitch from the seams and cuts mid-door to mid-door, so the
    middle tiles against itself and against both ends;
  * ramps each piece's gain across its own width so the pieces meet without a
    step in brightness: the middle matched to itself, each end ramped from its
    own outer edge to the middle's level at the join.

    python3 qa/cut_bench.py                 # all four, as configured below
    python3 qa/cut_bench.py b4              # just one

The printed `top` row goes into BENCH_SHEETS in expo.html.
"""
import sys, statistics
import numpy as np
from PIL import Image

ROOT = __file__.rsplit('/', 2)[0]
# era key -> (render, the row where the worktop's top surface ends, every-nth seam is a door)
JOBS = {
    'b1': ('Table_1.png', 180, 1),   # 1907–1979
    'b2': ('Table_3.png', 222, 1),   # 1980–1988
    'b3': ('Table_4.png', 205, 2),   # 1993–2007 — each door carries a groove, so every other seam
    'b4': ('Table_5.png', 182, 1),   # 2009–2026
}

def top_edge(a):
    m = a[..., 3] > 8
    t = np.argmax(m, axis=0).astype(np.float32)
    t[~m.any(axis=0)] = np.nan
    return t

def straighten(a, inner):
    """pull every column so the worktop's back edge is one straight line"""
    t = top_edge(a)
    T = float(np.nanmedian(t[inner[0]:inner[1]]))
    H = a.shape[0]
    out = a.copy()
    y = np.arange(H, dtype=np.float32)
    for x in range(a.shape[1]):
        tx = t[x]
        if not np.isfinite(tx) or abs(tx - T) < 0.5: continue
        # dst T -> src tx, dst bottom -> src bottom
        src = np.clip(tx + (y - T) * (H - 1 - tx) / max(1e-3, H - 1 - T), 0, H - 1)
        lo = np.floor(src).astype(int); hi = np.minimum(lo + 1, H - 1); f = (src - lo)[:, None]
        out[:, x] = a[lo, x] * (1 - f) + a[hi, x] * f
        out[:int(T), x] = 0
    return out, T

def edge_mean(a, side, w=8):
    col = a[:, :w, :3] if side == 'L' else a[:, -w:, :3]
    al = a[:, :w, 3] if side == 'L' else a[:, -w:, 3]
    m = al > 8
    return np.array([col[..., c][m].mean() for c in range(3)])

def ramp(a, gL, gR):
    t = np.linspace(0, 1, a.shape[1], dtype=np.float32)[None, :, None]
    out = a.copy()
    out[..., :3] = np.clip(out[..., :3] * (gL[None, None, :] * (1 - t) + gR[None, None, :] * t), 0, 255)
    return out

def cut(key):
    fn, lip, every = JOBS[key]
    im = Image.open(f'{ROOT}/Artefacts/{fn}').convert('RGBA')
    a = np.asarray(im).astype(np.float32)
    ys, xs = np.nonzero(a[..., 3] > 8)
    Y0, Y1, X0, X1 = ys.min(), ys.max(), xs.min(), xs.max()
    # the object's own edge is anti-aliased: a dozen rows of half-transparent
    # pixels top and bottom. Laid against the hall's floor that soft edge reads
    # as a pale line under the counter, so the crop is tightened to the rows
    # that are actually solid. 
    rowa = a[Y0:Y1 + 1, X0:X1 + 1, 3].mean(axis=1)
    solid = np.nonzero(rowa > 200)[0]
    Y0, Y1 = Y0 + solid[0], Y0 + solid[-1]
    a = a[Y0:Y1 + 1, X0:X1 + 1]
    n = a.shape[1]
    a, T = straighten(a, (int(.12 * n), int(.88 * n)))
    lip -= Y0
    H = a.shape[0]

    grey = a[..., :3].mean(axis=2)
    band = grey[lip + int(.2 * (H - lip)): lip + int(.8 * (H - lip))].mean(axis=0)
    m = float(np.median(band))
    seam = [x for x in range(3, n - 3) if band[x] < m - 12 and band[x] <= band[x-1] and band[x] <= band[x+1]]
    g, cur = [], [seam[0]]
    for x in seam[1:]:
        if x - cur[-1] <= 7: cur.append(x)
        else: g.append(sum(cur) // len(cur)); cur = [x]
    g.append(sum(cur) // len(cur))
    major = [g[0]]
    for x in g[1:]:
        if x - major[-1] >= 100: major.append(x)
    doors = major[0::every]
    d0 = [doors[i+1] - doors[i] for i in range(len(doors) - 1)]
    if d0[0] < 0.7 * statistics.median(d0): doors = doors[1:]
    pitch = round(statistics.median([doors[i+1] - doors[i] for i in range(len(doors) - 1)]))
    mid = lambda i: (doors[i] + doors[i+1]) // 2

    P = {'cap_l': a[:, 0:mid(0)], 'mid': a[:, mid(2):mid(2) + pitch], 'cap_r': a[:, mid(len(doors) - 2):]}
    L, R = edge_mean(P['mid'], 'L'), edge_mean(P['mid'], 'R')
    tgt = (L + R) / 2
    P['mid'] = ramp(P['mid'], tgt / L, tgt / R)
    one = np.ones(3, np.float32)
    P['cap_l'] = ramp(P['cap_l'], one, tgt / edge_mean(P['cap_l'], 'R'))
    P['cap_r'] = ramp(P['cap_r'], tgt / edge_mean(P['cap_r'], 'L'), one)

    U = (1080 - 700) / (H - lip)
    print(f'{key} <- {fn}:  {n}x{H}  кромка выпрямлена на строку {T:.0f}  дверей {len(doors)-1}  шаг {pitch} px')
    print(f'   BENCH_SHEETS: {{era: ?, key: \'{key}\', top: {lip}}}')
    for nm, arr in P.items():
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        img.save(f'{ROOT}/expo/assets/photo/bench_{key}_{nm}.png', optimize=True)
        img.save(f'{ROOT}/expo/assets/photo/bench_{key}_{nm}.webp', quality=94, method=6)
        print(f'   {nm:<6} {arr.shape[1]:>4}x{arr.shape[0]}  → {arr.shape[1]*U:6.1f} ед.')
    e = lambda p, s: edge_mean(P[p], s)
    lvl = e('mid', 'L').mean()
    print('   швы: торец→плитка %.2f%%  плитка→плитка %.2f%%  плитка→торец %.2f%%' % (
        100*abs(e('cap_l','R')-e('mid','L')).mean()/lvl,
        100*abs(e('mid','R')-e('mid','L')).mean()/lvl,
        100*abs(e('mid','R')-e('cap_r','L')).mean()/lvl))
    sk = top_edge(P['cap_l']); print('   перекос кромки торца: %.1f px' % (np.nanmax(sk)-np.nanmin(sk)))

for key in (sys.argv[1:] or JOBS):
    cut(key)
