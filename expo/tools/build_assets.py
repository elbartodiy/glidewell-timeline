#!/usr/bin/env python3
"""Собрать картинки зала в assets/img и переписать их список в expo.html.

Раньше этот скрипт вшивал их в страницу строкой base64. Так делать нельзя:
2,43 МБ из 3,38 МБ файла были картинками, гит не сжимает base64 между версиями,
и 452 версии expo.html дали 1,3 ГБ истории почти целиком на повторах одних и тех
же снимков (Эльдар, 2026-09-23). Теперь картинки — обычные файлы: каждая ложится
в историю по разу, а правка кода уносит туда килобайты, а не мегабайты.

ГДЕ ЛЕЖАТ ОРИГИНАЛЫ — ДЕЛО ЭЛЬДАРА. src/ это его шкаф, он его перекладывает, и
жёсткий путь тут ломается при каждой уборке. Имя файла — договор, полка — нет:
скрипт обходит src/ и берёт первый файл с нужным именем, пропуская src/audio.

ИМЯ В expo.html НЕ ВСЕГДА ИМЯ ФАЙЛА — обложки Chairside и кадр AI лежат под
своими родными именами; переименовывать чужой материал ради скрипта неправильно,
поэтому соответствие держит таблица ниже.

    python3 expo/tools/build_assets.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, '..', 'expo.html')
SRC  = os.path.join(HERE, '..', 'src')
OUT  = os.path.join(HERE, '..', 'assets', 'img')
SKIP = ('audio',)

ALIAS = {'chairv1': 'Chairside_1_1', 'chairv12': 'Chairside_12_3',
         'chairv21': 'Chairside_21_2', 'todayai': 'today-ai'}

# Зал рисует их мелко — самая крупная, обложка Chairside, идёт 147 px на кадре
# 2100 (293 на ретине). Больше 760 по длинной стороне держать незачем.
CAP, Q = 760, 86

def main():
    html = open(HTML, encoding='utf8').read()
    want = re.findall(r"([A-Za-z0-9_]+):'assets/img/[^']+'", html)
    if not want:
        sys.exit('список ASSETS в expo.html не найден')

    index = {}
    for root, dirs, files in os.walk(SRC):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for fn in files:
            nm, ext = os.path.splitext(fn)
            if ext.lower() in ('.jpg', '.jpeg', '.png'):
                index.setdefault(nm, os.path.join(root, fn))
    for key, fname in ALIAS.items():
        if key not in index and fname in index:
            index[key] = index[fname]

    missing = [n for n in want if n not in index]
    if missing:
        sys.exit('не найдены исходники в src/: ' + ', '.join(missing) + ' — ничего не менял')

    os.makedirs(OUT, exist_ok=True)
    rows, total = [], 0
    for nm in want:
        p = index[nm]
        raw = open(p, 'rb').read()
        if p.lower().endswith('.png'):
            out, ext = raw, 'png'
        else:
            try:
                from PIL import Image
                import io
                im = Image.open(p).convert('RGB')
                if max(im.size) > CAP:
                    k = CAP / max(im.size)
                    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
                buf = io.BytesIO()
                im.save(buf, 'JPEG', quality=Q, optimize=True, progressive=True)
                small = buf.getvalue()
                out = small if len(small) < len(raw) else raw
            except ImportError:
                out = raw
            ext = 'jpg'
        open(os.path.join(OUT, f'{nm}.{ext}'), 'wb').write(out)
        total += len(out)
        rows.append(f"{nm}:'assets/img/{nm}.{ext}'")

    head = re.search(r'//<ASSETS>.*?window\.ASSETS = \{', html, re.S).group(0)
    block = head[:head.index('window.ASSETS')] + 'window.ASSETS = {' + ',\n'.join(rows) + '};\n//</ASSETS>'
    html2, n = re.subn(r'//<ASSETS>.*?//</ASSETS>', lambda m: block, html, flags=re.S)
    if n != 1:
        sys.exit('маркеры ASSETS не найдены (или найдены дважды)')
    open(HTML, 'w', encoding='utf8').write(html2)
    print(f'{len(rows)} картинок, {total//1024}K файлами, expo.html '
          f'{os.path.getsize(HTML)//1024}K')

main()
