#!/usr/bin/env python3
"""
matte.py — turn a generated object image into a clean RGBA cutout.

Why this exists: image generators cannot output real alpha. They either draw a
"transparency" checkerboard as pixels, or put the object on flat white/chroma.
Thresholding such an image leaves a bright rim (the background bleeding through
semi-transparent edge pixels) — the halo that makes a composite read as pasted.

This tool models the background it knows: B(x,y) is a checkerboard, a flat
colour, or white. Every pixel is C = a*F + (1-a)*B, so once B is known both the
coverage a and the true object colour F can be solved for:

    a = clamp(|C-B| / T)          F = (C - (1-a)B) / a

That unmixing step is what removes the rim instead of hiding it. Chroma spill
is neutralised separately, the classic way (clamp the key channel to its
neighbours) so magenta never survives in chrome or glass.

Usage:
    python3 matte.py IN.png [IN2.png ...] --out DIR [--split] [--maxw 1200]

    --split   the sheet holds several projections side by side: cut them apart
              on background-only columns and matte each one separately.
"""
import argparse, os, sys
from collections import deque
import numpy as np
from PIL import Image


# ---------------------------------------------------------------- background

def detect_background(rgb):
    """Sample the border and decide what the background is."""
    h, w = rgb.shape[:2]
    band = np.concatenate([
        rgb[:6].reshape(-1, 3), rgb[-6:].reshape(-1, 3),
        rgb[:, :6].reshape(-1, 3), rgb[:, -6:].reshape(-1, 3)])
    med = np.median(band, axis=0)
    r, g, b = med
    spread = band.astype(int).std(axis=0).mean()

    # saturated key colour: one or two channels far above the rest
    mx, mn = med.max(), med.min()
    if mx - mn > 90 and mx > 140:
        # the MEASURED key, never the ideal one: a generated magenta is nearer
        # (247, 3, 238), and keying against pure #FF00FF leaves the difference
        # behind as a faint veil over the whole background
        if g < r - 80 and g < b - 80:  return ('chroma', med.astype(float), 1)   # magenta, green suppressed
        if r < g - 80 and b < g - 80:  return ('chroma', med.astype(float), 0)   # green key
    # checkerboard: two light tones in a regular grid -> high local variance
    if spread > 6 and med.min() > 170:
        return ('checker', None, None)
    if med.min() > 200:
        return ('flat', med.astype(float), None)
    return ('flat', med.astype(float), None)


def checker_model(rgb):
    """Rebuild the drawn transparency checkerboard as a per-pixel background.

    The cell size and phase are fitted, not assumed: a wrong phase inverts the
    whole model and every background pixel then reads as object. Candidates are
    scored on the border band only, which is cheap and is guaranteed to be
    background."""
    h, w = rgb.shape[:2]
    grey = rgb.mean(axis=2)
    border_mask = np.zeros((h, w), bool)
    border_mask[:10] = border_mask[-10:] = True
    border_mask[:, :10] = border_mask[:, -10:] = True
    bvals = grey[border_mask]
    hi, lo = np.percentile(bvals, 88), np.percentile(bvals, 12)
    mid = (hi + lo) / 2
    hi_rgb = np.median(rgb[border_mask & (grey > mid)].reshape(-1, 3), axis=0)
    lo_rgb = np.median(rgb[border_mask & (grey <= mid)].reshape(-1, 3), axis=0)

    # cell candidates from the run lengths along the top row
    row = grey[3] > mid
    runs, cur, prev = [], 1, row[0]
    for v in row[1:]:
        if v == prev: cur += 1
        else: runs.append(cur); cur = 1; prev = v
    runs.append(cur)
    runs = [r for r in runs if 2 < r < 96]
    base = int(np.median(runs)) if runs else 8
    cands = sorted({max(2, base), max(2, base // 2), min(96, base * 2), 8, 16, 24, 32})

    ys, xs = np.mgrid[0:h, 0:w]
    best = None
    for cell in cands:
        for ph in range(0, cell, max(1, cell // 4)):
            for flip in (0, 1):
                par = (((xs + ph) // cell) + ((ys + ph) // cell) + flip) % 2
                B = np.where(par[..., None] == 1, hi_rgb, lo_rgb)
                res = np.abs(rgb[border_mask] - B[border_mask]).mean()
                if best is None or res < best[0]:
                    best = (res, cell, ph, flip)
    res, cell, ph, flip = best
    par = (((xs + ph) // cell) + ((ys + ph) // cell) + flip) % 2
    B = np.where(par[..., None] == 1, hi_rgb, lo_rgb).astype(float)
    return B, abs(float(hi - lo)), res


def _box_std(a, r=3):
    """Local standard deviation over a (2r+1) window, via integral images."""
    a = a.astype(np.float64)
    pad = np.pad(a, r + 1, mode='edge')
    c1 = pad.cumsum(0).cumsum(1)
    c2 = (pad * pad).cumsum(0).cumsum(1)
    k = 2 * r + 1
    def win(c):
        return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k])[:a.shape[0], :a.shape[1]]
    n = k * k
    m = win(c1) / n
    v = np.maximum(win(c2) / n - m * m, 0)
    return np.sqrt(v)


def shadow_mask(rgb, B):
    """A baked drop shadow: neutral, only mildly darker than the background,
    and SMOOTH. The smoothness test is what protects bare metal, which is also
    neutral and mid-grey but always carries texture and specular detail."""
    lum, blum = rgb.mean(axis=2), B.mean(axis=2)
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    smooth = _box_std(lum, 3) < 4.5
    return (chroma < 14) & (lum > blum * 0.72) & (lum < blum * 1.04) & smooth


# ---------------------------------------------------------------- matting

def matte(img, maxw=1200):
    rgb = np.asarray(img.convert('RGB'), dtype=float)
    h, w = rgb.shape[:2]
    kind, key, keych = detect_background(rgb)

    if kind == 'checker':
        B, contrast, resid = checker_model(rgb)
        if resid > 12:            # the grid could not be fitted — treat as flat
            B = np.broadcast_to(np.median(rgb[:8].reshape(-1, 3), axis=0), rgb.shape).copy()
            tol = 26.0
        else:
            tol = max(16.0, contrast * 0.9)
    elif kind == 'chroma':
        B = np.broadcast_to(key, rgb.shape).copy()
        tol = 90.0
    else:
        B = np.broadcast_to(key, rgb.shape).copy()
        tol = 26.0

    # coverage from distance to the modelled background
    dist = np.linalg.norm(rgb - B, axis=2)
    a = np.clip((dist - tol * 0.35) / (tol * 0.9), 0.0, 1.0)

    # the generator bakes a soft drop shadow onto the background. The engine
    # casts its own contact shadow, so a baked one must go or it reads as a
    # pale smear on the dark bench. A shadow is neutral and merely a darkened
    # version of the background — never a colour the object owns.
    shadowish = shadow_mask(rgb, B)

    # A chroma key needs no connectivity test: the key colour is unambiguous, so
    # background enclosed by the object — the gap inside a lamp arm, the space
    # between a frame and its rail — is background too. White and checkerboard
    # backgrounds DO need it, because pale paper and plaster look like them.
    if kind == 'chroma':
        # Coverage from a DIFFERENCE key, not from distance to the key colour.
        # Distance lies about dark objects: a black edge half-covered by magenta
        # reads as (128,0,128), far from pure magenta, and would be called solid.
        # The difference key asks how much the key's own channels dominate the
        # suppressed one, which falls to zero on any real material.
        R, G, Bc = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        if keych == 1:                       # magenta: red and blue carry it
            bgness = np.minimum(R, Bc) - G
            span = min(B[0, 0, 0], B[0, 0, 2]) - B[0, 0, 1]
        else:                                # green key
            bgness = G - np.maximum(R, Bc)
            span = B[0, 0, 1] - max(B[0, 0, 0], B[0, 0, 2])
        a = np.clip(1.0 - bgness / max(span, 1.0), 0.0, 1.0)
        a[bgness > span * 0.92] = 0.0
        aa = np.clip(a, 1e-3, 1.0)[..., None]
        F = np.clip((rgb - (1.0 - aa) * B) / aa, 0, 255)
        # spill is a lighting effect; a generator paints a flat rectangle and the
        # object never reflects it, so only partly-covered edge pixels can carry
        # the key colour — the interior must be left exactly as drawn
        # A contaminated pixel is recognisable without guessing: magenta pushes
        # GREEN below both red and blue at once. Warm wood and beige marble keep
        # red > green > blue, so they never match and are never touched.
        if keych == 1:
            lo = np.minimum(F[..., 0], F[..., 2])
            excess = np.maximum(0.0, lo - F[..., 1] - 10.0)
            F[..., 0] -= excess * 0.95
            F[..., 2] -= excess * 0.95
        else:
            hi = np.maximum(F[..., 0], F[..., 2])
            excess = np.maximum(0.0, F[..., 1] - hi - 10.0)
            F[..., 1] -= excess * 0.95
        out = np.dstack([np.clip(F, 0, 255), a * 255.0]).astype(np.uint8)
        im = Image.fromarray(out)
        alpha = np.asarray(im)[..., 3]
        ys, xs = np.where(alpha > 8)
        if len(ys):
            im = im.crop((max(0, xs.min() - 2), max(0, ys.min() - 2),
                          min(w, xs.max() + 3), min(h, ys.max() + 3)))
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        return im, kind

    # connectivity: only background reachable from the border is really outside,
    # so light areas inside the object (labels, plaster, glass) stay opaque
    outside = np.zeros((h, w), bool)
    weak = (a < 0.35) | shadowish
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if weak[y, x] and not outside[y, x]: outside[y, x] = True; dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if weak[y, x] and not outside[y, x]: outside[y, x] = True; dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for ny, nx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
            if 0 <= ny < h and 0 <= nx < w and weak[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True; dq.append((ny, nx))
    a = np.where(outside, a, np.maximum(a, 0.999))
    # everything the flood reached is background: crumbs and baked shadow alike
    a[outside] = 0.0

    # UNMIX — the halo killer. F = (C - (1-a)B) / a
    aa = np.clip(a, 1e-3, 1.0)[..., None]
    F = (rgb - (1.0 - aa) * B) / aa
    F = np.clip(F, 0, 255)

    # chroma despill: the key channel may not exceed its neighbours
    if kind == 'chroma':
        if keych == 1:   # magenta: green is the key
            F[..., 0] = np.minimum(F[..., 0], (F[..., 1] + F[..., 2]) * 0.5 + 26)
            F[..., 2] = np.minimum(F[..., 2], (F[..., 1] + F[..., 0]) * 0.5 + 26)
        else:            # green key
            F[..., 1] = np.minimum(F[..., 1], (F[..., 0] + F[..., 2]) * 0.5 + 26)

    out = np.dstack([F, a * 255.0]).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA')

    # trim to the object
    alpha = np.asarray(im)[..., 3]
    ys, xs = np.where(alpha > 8)
    if len(ys):
        im = im.crop((max(0, xs.min() - 2), max(0, ys.min() - 2),
                      min(w, xs.max() + 3), min(h, ys.max() + 3)))
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    return im, kind


def split_views(img, views=0):
    """Cut a multi-projection sheet on background-only columns.

    With `views` given (these sheets are always three projections), the cut is
    made at the N-1 widest background gaps — deterministic, and immune to the
    narrow gaps inside a single object (a detached kiln door, a row of jars)."""
    rgb = np.asarray(img.convert('RGB'), dtype=float)
    kind, key, _ = detect_background(rgb)
    B = checker_model(rgb)[0] if kind == 'checker' else np.broadcast_to(key, rgb.shape).copy()
    dist = np.linalg.norm(rgb - B, axis=2)
    # a baked drop shadow bridges the gap between two projections; it must not
    # weld them into one view, so shadow pixels count as background here too
    objish = (dist >= 16) & ~shadow_mask(rgb, B)
    is_bg = ~objish.any(axis=0)
    spans, start = [], None
    for x, bg in enumerate(is_bg):
        if not bg and start is None: start = x
        elif bg and start is not None: spans.append([start, x]); start = None
    if start is not None: spans.append([start, len(is_bg)])
    merged = []
    for s in spans:
        if merged and s[0] - merged[-1][1] < 24: merged[-1][1] = s[1]
        else: merged.append(s)
    merged = [m for m in merged if m[1] - m[0] > 50]
    if views and len(merged) > 1:
        gaps = sorted(((merged[i+1][0] - merged[i][1], i) for i in range(len(merged) - 1)), reverse=True)
        cuts = sorted(i for _, i in gaps[:views - 1])
        grouped, start = [], 0
        for c in cuts + [len(merged) - 1]:
            grouped.append([merged[start][0], merged[c][1]]); start = c + 1
        merged = grouped
    return [img.crop((max(0, a - 8), 0, min(img.width, b + 8), img.height)) for a, b in merged] or [img]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inputs', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--split', action='store_true')
    ap.add_argument('--views', type=int, default=0, help='sheet holds exactly N projections')
    ap.add_argument('--maxw', type=int, default=1200)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for path in args.inputs:
        base = os.path.splitext(os.path.basename(path))[0]
        img = Image.open(path)
        views = split_views(img, args.views) if (args.split or args.views) else [img]
        for i, v in enumerate(views):
            cut, kind = matte(v, args.maxw)
            name = f'{base}.png' if len(views) == 1 else f'{base}_{i}.png'
            cut.save(os.path.join(args.out, name))
            print(f'{name}  bg={kind}  {cut.width}x{cut.height}')


if __name__ == '__main__':
    main()
