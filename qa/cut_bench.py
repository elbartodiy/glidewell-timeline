#!/usr/bin/env python3
"""Cut a counter render into the four pieces the hall lays it from.

Eldar's rule (2026-09-21): a counter is four parts — the left end, the short
block (a door), the long block the width of the caption, and the right end. He
renders exactly that: end | door | door | LONG PANEL | door | door | end, all
four eras on the same canvas. This takes the render and cuts it there.

NOTHING IS REDRAWN. The geometry comes off the file as it is — no straightening
of the worktop's back edge (the new renders are already flat across the middle,
and the rise in the last sixty columns is the end return's own perspective), no
gain ramps. The only two things done to the pixels are a crop and a cut:

  * the bounding box is taken from the ALPHA — the renders are transparent PNGs
    and flattening them to RGB bakes the studio ground in behind the furniture;
  * the crop is tightened to the rows that are actually solid, because the
    render's own edge is anti-aliased and against the hall's floor a dozen rows
    of half-transparent pixels read as a pale line under the counter.

The six seams are found in the file: the columns where the front is darkest,
kept by prominence, and the strongest six are the ends and the doors.

    python3 qa/cut_bench.py                 # all four, as configured below
    python3 qa/cut_bench.py b4              # just one

The printed `top` row goes into BENCH_SHEETS in expo.html.
"""
import sys
import numpy as np
from PIL import Image

ROOT = __file__.rsplit('/', 2)[0]
JOBS = {
    'b1': 'Table_1.png',   # 1907–1979
    'b2': 'Table_3.png',   # 1980–1988
    'b3': 'Table_4.png',   # 1993–2007
    'b4': 'Table_5.png',   # 2009–2026
}

def seams(face):
    """the six cut columns: two ends and four door joints, found in the file.

    A seam is a dark line with LIGHTER material on both sides, which is what
    separates it from the render's own silhouette edge — that is just as dark
    but has nothing to its outside, so its two-sided prominence is small."""
    band = face.mean(axis=0)
    w, n = 40, len(band)
    d = np.zeros(n)
    for x in range(1, n - 1):
        l, r = band[max(0, x - w):x], band[x + 1:x + 1 + w]
        if len(l) and len(r): d[x] = min(l.max(), r.max()) - band[x]
    cand = [x for x in range(3, n - 3) if d[x] > 6 and band[x] == band[x - 3:x + 4].min()]
    cand.sort(key=lambda x: -d[x])
    keep = []
    for x in cand:                                    # one column per seam
        if all(abs(x - y) > 45 for y in keep): keep.append(x)
    lim = 0.45 * max(d[x] for x in keep)              # the grooves in a door are half as dark
    return sorted(x for x in keep if d[x] >= lim)

def lip_row(a):
    """the row where the worktop's TOP SURFACE ends and the front begins.

    Every one of the renders lights the slab's front arris — a bright line
    along the whole length — so the surface ends where that line starts. This
    is NOT the bottom of the slab: the thickness of the worktop belongs to the
    front elevation, and the hall stands the top surface at bench height."""
    n, H = a.shape[1], a.shape[0]
    col = a[:, int(.38 * n):int(.62 * n), :3].mean(axis=2).mean(axis=1)
    lo, hi = 8, int(.12 * H)   # the diode light in the 2009 counter is brighter still
    r = lo + int(np.argmax(col[lo:hi]))
    base = float(np.median(col[2:lo + 4]))
    lim = base + .4 * (col[r] - base)
    while r > 2 and col[r - 1] > lim: r -= 1
    return r

def cut(key):
    fn = JOBS[key]
    a = np.asarray(Image.open(f'{ROOT}/Artefacts/{fn}').convert('RGBA')).astype(np.float32)
    ys, xs = np.nonzero(a[..., 3] > 8)
    Y0, Y1, X0, X1 = ys.min(), ys.max(), xs.min(), xs.max()
    rowa = a[Y0:Y1 + 1, X0:X1 + 1, 3].mean(axis=1)
    solid = np.nonzero(rowa > 200)[0]
    a = a[Y0 + solid[0]:Y0 + solid[-1] + 1, X0:X1 + 1]
    H, n = a.shape[0], a.shape[1]
    lip = lip_row(a)

    grey = a[..., :3].mean(axis=2)
    s = seams(grey[lip + int(.22 * (H - lip)): lip + int(.78 * (H - lip))])
    if len(s) != 6:
        print(f'{key}: нашлось {len(s)} швов вместо шести — {s}'); return
    # end | door | door | LONG | door | door | end.  Every piece but the left end
    # begins WITH its own seam column, so a piece laid against the next one puts
    # the seam back exactly once — a joint that reads as the cabinet's own.
    P = {'cap_l': a[:, 0:s[0]], 'mid': a[:, s[1]:s[2]],
         'long': a[:, s[2]:s[3]], 'cap_r': a[:, s[5]:]}

    U = (1080 - 700) / (H - lip)                      # world units per image column
    print(f'{key} <- {fn}:  {n}x{H}  швы {s}')
    print(f"   BENCH_SHEETS: {{era: ?, key: '{key}', top: {lip}}}")
    for nm, arr in P.items():
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        img.save(f'{ROOT}/expo/assets/photo/bench_{key}_{nm}.png', optimize=True)
        img.save(f'{ROOT}/expo/assets/photo/bench_{key}_{nm}.webp', quality=94, method=6)
        print(f'   {nm:<6} {arr.shape[1]:>4}x{arr.shape[0]}  → {arr.shape[1] * U:6.1f} ед.')
    def edge(p, side, w=10):
        arr = P[p]
        o = min(12, max(2, arr.shape[1] // 3 - w))     # clear of the seam's own shadow
        sl = arr[:, o:o + w, :3] if side == 'L' else arr[:, -w - o:-o, :3]
        al = arr[:, o:o + w, 3] if side == 'L' else arr[:, -w - o:-o, 3]
        m = al > 200
        return np.array([sl[..., c][m].mean() for c in range(3)])
    lvl = edge('mid', 'L').mean()
    print('   яркость на стыках: торец→дверца %.2f%%  дверца→дверца %.2f%%  '
          'дверца→панель %.2f%%  панель→дверца %.2f%%  дверца→торец %.2f%%' % tuple(
        100 * abs(x - y).mean() / lvl for x, y in (
            (edge('cap_l', 'R'), edge('mid', 'L')), (edge('mid', 'R'), edge('mid', 'L')),
            (edge('mid', 'R'), edge('long', 'L')), (edge('long', 'R'), edge('mid', 'L')),
            (edge('mid', 'R'), edge('cap_r', 'L')))))
    print('   длинная панель = %.2f дверцы' % (P['long'].shape[1] / P['mid'].shape[1]))

for key in (sys.argv[1:] or JOBS):
    cut(key)
