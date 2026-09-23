#!/usr/bin/env python3
"""Соберать расписание курсов Glidewell в компактный expo/data/events.json.

Почему не напрямую из браузера: магазин (Shopify) отдаёт JSON без заголовка
Access-Control-Allow-Origin, поэтому fetch с нашей страницы браузер заблокирует.
И это к лучшему: зал может стоять на машине в здании, а стенд, зависящий от
живого запроса наружу, однажды погаснет. Файл лежит рядом с залом, обновляется
скриптом (руками или по расписанию в CI), а зал читает свой собственный файл.

    python3 expo/tools/fetch_events.py

Источник — коллекция education витрины glidewelldirect.com: там каждая дата
курса это отдельный «вариант товара», с городом, ценой и наличием мест.
"""
import json, os, re, sys, urllib.request
from datetime import datetime, date

SRC = 'https://glidewelldirect.com/collections/education/products.json?limit=250'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'events.json')

MONTHS = {m: i for i, m in enumerate(
    ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'], 1)}

def parse_when(t):
    """«Oct. 30–31, 2026 (Irvine, CA) / $795 per Doctor» -> (2026-10-30, 2026-10-31)."""
    m = re.match(r'\s*([A-Za-z]+)\.?\s*(\d+)\s*(?:[–-]\s*(\d+))?\s*,\s*(\d{4})', t)
    if not m:
        return None, None
    mon = MONTHS.get(m.group(1)[:3].lower())
    if not mon:
        return None, None
    y = int(m.group(4)); d1 = int(m.group(2)); d2 = int(m.group(3) or d1)
    try:
        a = date(y, mon, d1); b = date(y, mon, d2)
    except ValueError:
        return None, None
    return a.isoformat(), b.isoformat()

def tag(tags, prefix):
    return [t.split('_', 1)[1] for t in tags if t.startswith(prefix)]

def main():
    raw = json.load(urllib.request.urlopen(SRC, timeout=30))
    today = date.today().isoformat()
    rows = []
    for p in raw.get('products', []):
        instructors = tag(p['tags'], 'Instructor_')
        duration = (tag(p['tags'], 'Course Duration_') or [''])[0]
        for v in p['variants']:
            # одна дата продаётся несколькими билетами (врач / врач+отель /
            # ассистент) — берём только врачебный, иначе доска утроится
            if 'staff' in v['title'].lower() or 'hotel' in v['title'].lower():
                continue
            d1, d2 = parse_when(v['title'])
            if not d1 or d1 < today:
                continue
            city = (re.search(r'\(([^)]+)\)', v['title']) or [None, ''])[1]
            rows.append({
                'title': p['title'],
                'from': d1, 'to': d2,
                'city': city,
                'kind': 'Symposium' if 'symposium' in p['title'].lower() else 'Live course',
                'instructors': instructors,
                'duration': duration,
                'price': v.get('price'),
                'open': bool(v.get('available')),
                'url': f"https://glidewelldirect.com/products/{p['handle']}?variant={v['id']}",
            })
    rows.sort(key=lambda r: (r['from'], r['city']))
    out = {'updated': datetime.now().astimezone().isoformat(timespec='seconds'),
           'source': SRC, 'count': len(rows), 'events': rows}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(f'{len(rows)} дат, ближайшая {rows[0]["from"]} ({rows[0]["city"]}), '
          f'последняя {rows[-1]["from"]}')

main()
