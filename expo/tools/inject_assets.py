#!/usr/bin/env python3
"""Regenerate the base64 asset block inside expo.html from expo/assets/*.jpg.
Idempotent: replaces everything between //<ASSETS> and //</ASSETS> markers."""
import base64, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, '..', 'expo.html')
ASSETS = os.path.join(HERE, '..', 'assets')

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
out, n = re.subn(r'//<ASSETS>.*?//</ASSETS>', lambda m: block, src, flags=re.S)
if n != 1:
    sys.exit('ASSETS markers not found (or found twice)')
open(HTML, 'w', encoding='utf8').write(out)
print(f'injected {len(entries)} assets, {total//1024}K raw, html now {os.path.getsize(HTML)//1024}K')
