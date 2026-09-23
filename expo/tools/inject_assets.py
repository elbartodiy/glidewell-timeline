#!/usr/bin/env python3
"""Regenerate the base64 asset block inside expo.html from expo/assets/_src.

The sources live in assets/_src now, out of the way of the four folders the
hall actually reads at runtime (photo, people, album, fonts). They are the
originals of the pictures already inlined in expo.html; nothing loads them.

AND IT REFUSES TO SHRINK THE BLOCK. It replaces the whole block, so a source
folder that has gone missing — moved, emptied, tidied away — used to mean an
empty block and forty-three pictures out of the hall in one run (Eldar,
2026-09-23, asking whether he could delete them). If there are fewer files than
there are entries already in the html, it stops and says so."""
import base64, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, '..', 'expo.html')
ASSETS = os.path.join(HERE, '..', 'assets', '_src')

entries = []
total = 0
for p in sorted(glob.glob(os.path.join(ASSETS, '*.jpg')) + glob.glob(os.path.join(ASSETS, '*.png'))):
    name = os.path.splitext(os.path.basename(p))[0]
    raw = open(p, 'rb').read()
    total += len(raw)
    mime = 'image/png' if p.endswith('.png') else 'image/jpeg'
    entries.append(f'{name}:"data:{mime};base64,{base64.b64encode(raw).decode()}"')

block = '//<ASSETS>\nwindow.ASSETS = {' + ',\n'.join(entries) + '};\n//</ASSETS>'
src = open(HTML, encoding='utf8').read()
have = src.count(':"data:image')      # the first entry shares its line with the opening brace
if len(entries) < have:
    sys.exit(f'refusing: {len(entries)} files in {ASSETS} but {have} already inlined — '
             f'the sources have moved or been removed, and this would strip the hall')
out, n = re.subn(r'//<ASSETS>.*?//</ASSETS>', lambda m: block, src, flags=re.S)
if n != 1:
    sys.exit('ASSETS markers not found (or found twice)')
open(HTML, 'w', encoding='utf8').write(out)
print(f'injected {len(entries)} assets, {total//1024}K raw, html now {os.path.getsize(HTML)//1024}K')
