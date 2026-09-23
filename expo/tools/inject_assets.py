#!/usr/bin/env python3
"""Regenerate the base64 asset block inside expo.html from the pictures in src/.

WHERE THE SOURCES ARE IS ELDAR'S BUSINESS. src/ is his cupboard and he
rearranges it — these forty-three were loose in assets/, then assets/_src, then
src/pictures, and are now sorted into folders of his own inside it. So this
does not walk a path: it takes the names already inlined in expo.html and finds
each one anywhere under src/, ignoring the renders (which are cut by other
scripts and must never be inlined) and the audio.

AND IT REFUSES TO SHRINK THE BLOCK. It replaces the block whole, so a source
that has gone missing used to mean that picture out of the hall. If any name
cannot be found it names it and stops, having changed nothing.

A NEW picture is added by putting the file under src/ and naming it in
expo.html's ASSETS block first — or by passing --add name.jpg.
"""
import base64, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, '..', 'expo.html')
SRC  = os.path.join(HERE, '..', 'src')
SKIP = ('audio',)                       # nothing here is a picture for the hall

src_txt = open(HTML, encoding='utf8').read()
want = re.findall(r'([A-Za-z0-9_]+):"data:image/(jpeg|png);base64', src_txt)
if not want:
    sys.exit('ASSETS block not found in expo.html')
for extra in sys.argv[1:]:
    if extra.startswith('--add='):
        nm = os.path.splitext(os.path.basename(extra[6:]))[0]
        want.append((nm, 'png' if extra.endswith('.png') else 'jpeg'))

index = {}
for root, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in SKIP]
    for fn in files:
        nm, ext = os.path.splitext(fn)
        if ext.lower() in ('.jpg', '.jpeg', '.png'):
            index.setdefault(nm, os.path.join(root, fn))

missing = [nm for nm, _ in want if nm not in index]
if missing:
    sys.exit('не найдены исходники в src/: ' + ', '.join(missing) + ' — ничего не менял')

entries, total = [], 0
for nm, kind in want:
    p = index[nm]
    raw = open(p, 'rb').read()
    total += len(raw)
    mime = 'image/png' if p.lower().endswith('.png') else 'image/jpeg'
    entries.append(f'{nm}:"data:{mime};base64,{base64.b64encode(raw).decode()}"')

block = '//<ASSETS>\nwindow.ASSETS = {' + ',\n'.join(entries) + '};\n//</ASSETS>'
out, n = re.subn(r'//<ASSETS>.*?//</ASSETS>', lambda m: block, src_txt, flags=re.S)
if n != 1:
    sys.exit('ASSETS markers not found (or found twice)')
open(HTML, 'w', encoding='utf8').write(out)
print(f'injected {len(entries)} assets, {total//1024}K raw, html now {os.path.getsize(HTML)//1024}K')
