#!/usr/bin/env python3
"""
make_wall.py — procedural, seamlessly tileable wall textures for the hall.

Built from the archive photographs of Jim's first lab: a sprayed/knockdown
plaster in warm cream, fine irregular specks over a slow mottle, with sparse
vertical joints where the boards meet. Generating it beats photographing it —
a tile has to repeat along thirty thousand world units without ever showing a
seam, which no single render can promise.

Tileability comes from building the noise in the frequency domain: an FFT of
white noise shaped by 1/f^beta and transformed back is periodic by
construction, so the left edge already continues into the right one.

    python3 make_wall.py --preset plaster70 --out ../assets/photo/wall_e1.jpg
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter


def fractal(h, w, beta, seed):
    """Periodic 1/f^beta noise, normalised to zero mean and unit variance."""
    rng = np.random.default_rng(seed)
    F = np.fft.fft2(rng.normal(size=(h, w)))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    r = np.sqrt(fy ** 2 + fx ** 2)
    r[0, 0] = 1.0
    F *= r ** (-beta)
    out = np.real(np.fft.ifft2(F))
    return (out - out.mean()) / (out.std() + 1e-9)


PRESETS = {
    # the 1970 lab: sprayed plaster, warm cream, dark board joints
    'plaster70': dict(base=(214, 201, 178), mottle=0.028, speck=0.20, speck_thr=0.55,
                      grain=0.020, joint_every=470, joint_dark=0.16, joint_soft=3),
    # 1980s: painted panel, cooler and flatter
    'panel80':   dict(base=(178, 176, 158), mottle=0.040, speck=0.040, speck_thr=1.25,
                      grain=0.012, joint_every=300, joint_dark=0.20, joint_soft=2),
    # 1990s–2000s: matte office board
    'board90':   dict(base=(168, 171, 166), mottle=0.030, speck=0.028, speck_thr=1.40,
                      grain=0.010, joint_every=0, joint_dark=0.18, joint_soft=2),
    # the white era
    'white20':   dict(base=(226, 229, 232), mottle=0.018, speck=0.014, speck_thr=1.70,
                      grain=0.007, joint_every=0, joint_dark=0.10, joint_soft=2),
}


def make(preset, w, h, seed):
    p = PRESETS[preset]
    # slow blotching — decades of light and cleaning
    lum = 1.0 + fractal(h, w, 1.7, seed) * p['mottle']
    # the sprayed specks: near-white noise, thresholded into grains, softened
    sp = fractal(h, w, 0.30, seed + 1)
    dots = np.clip(sp - p['speck_thr'], 0, None)
    dots = np.clip(dots / 0.9, 0, 1)
    dots = np.asarray(Image.fromarray((dots * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(0.55))) / 255.0
    lum -= dots * p['speck']
    pits = np.clip(-sp - p['speck_thr'] - 0.25, 0, None)
    lum += np.clip(pits, 0, 1) * p['speck'] * 0.45
    # fine tooth
    lum += fractal(h, w, 0.05, seed + 2) * p['grain']

    # vertical joints between boards, with a hair of light on one side
    if p['joint_every']:
        xs = np.arange(w)
        for x0 in range(p['joint_every'] // 2, w, p['joint_every']):
            d = np.minimum(np.abs(xs - x0), w - np.abs(xs - x0))     # wrap-aware distance
            lum -= p['joint_dark'] * np.exp(-(d / p['joint_soft']) ** 2)[None, :]
            lum += p['joint_dark'] * 0.28 * np.exp(-((d - p['joint_soft'] * 2.2) / (p['joint_soft'] * 1.6)) ** 2)[None, :]

    base = np.array(p['base'], float)[None, None, :]
    rgb = np.clip(base * lum[..., None], 0, 255)
    return Image.fromarray(rgb.astype(np.uint8))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='plaster70', choices=sorted(PRESETS))
    ap.add_argument('--width', type=int, default=2048)
    ap.add_argument('--height', type=int, default=1024)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    img = make(a.preset, a.width, a.height, a.seed)
    img.save(a.out, quality=94)
    print(f'{a.out}  {a.width}x{a.height}  preset={a.preset}  (tileable)')


if __name__ == '__main__':
    main()
