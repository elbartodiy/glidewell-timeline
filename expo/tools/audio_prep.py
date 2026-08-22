#!/usr/bin/env python3
"""
audio_prep.py — turn six similar generated tracks into six rooms.

Suno converged: the six pieces share a spectrum (top band 0.04-0.10 of the
energy on every one of them) and their characteristic material sits at a
different minute in each. Regenerating fights that; shaping does not. So:

  1. LIFT — each track is cut to the minute that is least like the average of
     all six, measured on an eight-band spectral profile. That is the part
     that actually sounds like itself.
  2. LOOP — the tail is crossfaded back over the head with an equal-power
     curve, so the piece can run for hours without a visible joint.
  3. ROOM — each era gets its own tone curve, applied in the frequency domain:
     the craft years lose their top and gain wood; the mail-order years get
     cassette wobble and hiss; the first digital lab is thinned at the bottom
     and given a bell-range lift; the white era opens up. This is what makes
     six similar pieces read as six different rooms.
  4. LEVEL — everything lands at the same quiet RMS, well under any speech.

Usage:
    python3 audio_prep.py --in expo/audio --out expo/audio
"""
import argparse, os, subprocess, tempfile, wave
import numpy as np

SR = 44100

# era -> (source file, tone recipe)
PLAN = [
    ('mus_welcome', '1.mp3', dict(lp=2600, tilt=-2.0, warm=0.10, air=0.0,  hiss=0.0,  wobble=0.0,   crush=0, hp=40,  gain=-4.0)),
    ('mus_era1',    '2.mp3', dict(lp=3400, tilt=-3.0, warm=0.22, air=0.0,  hiss=0.6,  wobble=0.0032, crush=0, hp=45, gain=-1.0)),
    ('mus_era2',    '3.mp3', dict(lp=6000, tilt=-1.0, warm=0.12, air=0.05, hiss=1.0,  wobble=0.0018, crush=0, hp=55, gain=-1.0)),
    ('mus_era3',    '4.mp3', dict(lp=8000, tilt= 0.5, warm=0.00, air=0.10, hiss=0.25, wobble=0.0006, crush=9, hp=95, gain=-1.0)),
    ('mus_era4',    '5.mp3', dict(lp=15000, tilt= 1.5, warm=0.00, air=0.32, hiss=0.0, wobble=0.0,   crush=0, hp=70, gain=-1.0)),
    ('mus_finale',  '6.mp3', dict(lp=11000, tilt= 0.8, warm=0.10, air=0.22, hiss=0.0, wobble=0.0,   crush=0, hp=55, gain=-2.0)),
]
WIN = 60.0          # seconds of loop material
XF  = 5.0           # crossfade for the seamless loop
TARGET_RMS_DB = -22.0


def decode(path):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as t:
        tmp = t.name
    subprocess.run(['afconvert', '-f', 'WAVE', '-d', f'LEI16@{SR}', '-c', '2', path, tmp],
                   check=True, capture_output=True)
    w = wave.open(tmp, 'rb')
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    ch = w.getnchannels(); w.close(); os.unlink(tmp)
    return a.reshape(-1, ch) if ch > 1 else np.stack([a, a], axis=1)


def profile(x, sr=SR, hop=None):
    """eight-band spectral profile per 250 ms frame"""
    hop = hop or sr // 4
    m = x.mean(axis=1)
    fr = m[:len(m) // hop * hop].reshape(-1, hop)
    sp = np.abs(np.fft.rfft(fr * np.hanning(hop), axis=1))
    f = np.fft.rfftfreq(hop, 1 / sr)
    edges = [0, 120, 250, 500, 900, 1500, 2400, 4000, sr / 2]
    b = np.stack([sp[:, (f >= edges[i]) & (f < edges[i + 1])].sum(axis=1) for i in range(8)], axis=1)
    return b / (b.sum(axis=1, keepdims=True) + 1e-9), np.sqrt((fr ** 2).mean(axis=1))


def pick_window(prof, rms, glob, win_frames):
    best, at = -1, 0
    for s in range(0, max(1, len(prof) - win_frames), 8):
        seg = prof[s:s + win_frames]
        if len(seg) < win_frames:
            break
        d = np.abs(seg.mean(axis=0) - glob).sum() + 0.4 * seg.std(axis=0).sum()
        if rms[s:s + win_frames].min() < 0.004:
            d *= 0.4                      # never loop across a hole of silence
        if d > best:
            best, at = d, s
    return at


def tone(x, r):
    """the era's room, drawn as a frequency response and applied by FFT"""
    n = len(x)
    F = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(n, 1 / SR)[:, None]
    g = np.ones_like(f)
    g *= 1.0 / (1.0 + (f / r['lp']) ** 2) ** 0.9                     # top rolled off
    g *= (f / (f + r['hp'])) ** 1.2                                  # bottom tightened
    g *= 10 ** ((r['tilt'] * np.log2((f + 40) / 500) / 6) / 20)      # overall tilt
    g *= 1 + r['warm'] * np.exp(-((np.log2((f + 20) / 260)) ** 2) / 0.5)   # wood
    g *= 1 + r['air']  * np.exp(-((np.log2((f + 20) / 7000)) ** 2) / 1.2)  # air
    return np.fft.irfft(F * g, n=n, axis=0)


def wobble(x, depth):
    """tape: a slow drift in speed, the sound of a machine that is not digital"""
    if depth <= 0:
        return x
    n = len(x)
    t = np.arange(n)
    d = depth * (np.sin(2 * np.pi * 0.7 * t / SR) + 0.6 * np.sin(2 * np.pi * 0.23 * t / SR))
    idx = np.clip(t + d * SR * 0.02, 0, n - 1)
    return np.stack([np.interp(idx, t, x[:, c]) for c in range(x.shape[1])], axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='src', default='expo/audio')
    ap.add_argument('--out', dest='dst', default='expo/audio')
    a = ap.parse_args()

    tracks = {}
    for name, fn, _ in PLAN:
        p = os.path.join(a.src, fn)
        if not os.path.exists(p):
            print(f'!! missing {p}'); continue
        tracks[name] = decode(p)

    profs = {k: profile(v) for k, v in tracks.items()}
    glob = np.mean([p[0].mean(axis=0) for p in profs.values()], axis=0)
    win_frames = int(WIN * 4)

    for name, fn, r in PLAN:
        if name not in tracks:
            continue
        x = tracks[name]
        pr, rms = profs[name]
        s = pick_window(pr, rms, glob, win_frames) * (SR // 4)
        seg = x[s:s + int(WIN * SR)]
        if len(seg) < int(WIN * SR):
            seg = x[-int(WIN * SR):]

        seg = tone(seg, r)
        seg = wobble(seg, r['wobble'])
        if r['crush']:
            q = 2 ** r['crush']
            seg = np.round(seg * q) / q
        if r['hiss']:
            noise = np.random.default_rng(7).normal(0, 1, seg.shape).astype(np.float32)
            noise = tone(noise, dict(lp=9000, hp=900, tilt=0, warm=0, air=0))
            seg = seg + noise * (r['hiss'] * 0.0016)

        # seamless loop: the tail is folded back over the head, equal power
        xf = int(XF * SR)
        head, tail = seg[:xf], seg[-xf:]
        w = np.linspace(0, 1, xf)[:, None]
        seg = np.concatenate([head * np.sqrt(w) + tail * np.sqrt(1 - w), seg[xf:-xf]])

        cur = 20 * np.log10(np.sqrt((seg ** 2).mean()) + 1e-9)
        seg *= 10 ** ((TARGET_RMS_DB + r['gain'] - cur) / 20)
        peak = np.abs(seg).max()
        if peak > 0.89:
            seg *= 0.89 / peak

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as t:
            tmp = t.name
        w16 = wave.open(tmp, 'wb'); w16.setnchannels(2); w16.setsampwidth(2); w16.setframerate(SR)
        w16.writeframes((np.clip(seg, -1, 1) * 32767).astype('<i2').tobytes()); w16.close()
        out = os.path.join(a.dst, name + '.m4a')
        subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', '128000', tmp, out],
                       check=True, capture_output=True)
        os.unlink(tmp)
        print(f'{out}  from {fn} @ {s/SR:5.1f}s  {len(seg)/SR:.1f}s  '
              f'rms {20*np.log10(np.sqrt((seg**2).mean())):.1f} dB')


if __name__ == '__main__':
    main()
