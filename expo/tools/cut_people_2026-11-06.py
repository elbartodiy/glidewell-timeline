# Портреты для страницы «The voices» — одиннадцати человек из тридцати восьми
# лица не было вовсе (Эльдар, 06.11.2026: «смело ищи их лица, ставь и просто
# мне покажи, какие ты поставил с именами, я уже проконтролирую сам»).
#
# Найдено восемь. Источник у каждого записан рядом — проверять по нему.
# Снимки лежат в scratchpad и в репозиторий не кладутся: здесь остаются
# ТОЛЬКО обрезанные 360×450, как у прежних двадцати семи.
#
#   ceranic   Dzevad Ceranic   — LinkedIn, профильное фото
#                                («Dzevad Ceranic, CDT – Glidewell Dental»)
#   withrow   Darryl Withrow   — LinkedIn, профильное фото
#                                («Darryl Withrow – Executive Vice President at Glidewell Dental»)
#   fejzagic  Leila Fejzagic   — ENP Institute, страница спикера («Leila G. Fejzagic»)
#   brenneise Rob Brenneise    — контактная карточка Glidewell: на ней его снимок
#                                и подпись «Contact Robert Brenneise /
#                                Robert.Brenneise@glidewelldental.com» — вырезан
#                                прямоугольник снимка (935…1455 × 490…1140)
#   marie     Marie Alejandrino-Buell — WebMD, «Dr. Marie Alejandro-Buell, DDS,
#                                Dentist | Oxnard, CA»
#   sohn      Joon Woo Sohn    — сайт его практики, страница Meet The Doctor:
#                                jwdentistryla.smcnational.com/meet-the-doctor/
#   wali      Teena Wali       — Doctor.com, «Dr. Teena Wali, DDS – La Habra, CA»
#   julio     Julio Terra      — сайт его практики smilethespa.com,
#                                alt «Dr Julio Terra Cosmetic Dentist»
#
# Не нашёл и, скорее всего, не найти: Joan и Dr. June — в данных только имя без
# фамилии; Paula LaBar — публично ничего. Их снимки есть только у Эльдара.
#
# Обрезка: доля исходника → 4:5 → 360×450, как прежние портреты.
from PIL import Image
import os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/faces')
DST = 'assets/people'

# id: (файл, левый, верхний, правый, нижний) — в долях исходника
CUT = {
    'ceranic':   ('ceranic_big.jpg',   0.00, 0.00, 0.80, 1.00),
    'withrow':   ('withrow_big.jpg',   0.00, 0.00, 0.80, 1.00),
    'fejzagic':  ('fejzagic_big.jpg',  0.10, 0.00, 0.90, 1.00),
    'marie':     ('marie_b.jpg',       0.10, 0.00, 0.90, 1.00),
    'wali':      ('wali_a.jpg',        0.089, 0.00, 0.889, 1.00),
    'brenneise': ('brenneise_big.jpg', 0.5956, 0.3138, 0.8994, 0.6938),   # ровно по тёмному прямоугольнику снимка: 953…1439 × 502…1110
    'sohn':      ('sohn_a.webp',       0.3201, 0.0174, 0.6597, 0.3594),   # портретный план: голова 75…375, плечи до 620
    'julio':     ('julio_site.jpg',    0.2472, 0.0000, 0.7520, 0.4734),
}

for pid, (f, l, t, r, b) in CUT.items():
    im = Image.open(os.path.join(SRC, f)).convert('RGB')
    W, H = im.size
    box = (round(l * W), round(t * H), round(r * W), round(b * H))
    out = im.crop(box)
    # ровно 4:5 — подрезаем по короткой стороне, не растягивая
    w, h = out.size
    if w / h > 0.8:
        nw = round(h * 0.8); out = out.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = round(w / 0.8); out = out.crop((0, 0, w, min(h, nh)))
    out = out.resize((360, 450), Image.LANCZOS)
    out.save(os.path.join(DST, pid + '.jpg'), quality=86, optimize=True)
    print('%-10s %s %s -> 360x450' % (pid, f, box))
