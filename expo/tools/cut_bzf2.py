# Нарезка новых деталей фабрики BruxZir (Эльдар, 02.11.2026: «я тут обновил детали»).
# Каждая деталь режется по своему окну в точках исходника и уменьшается в scale раз —
# ровно так же, как резались r_bzf_* 29.10.2026.
#
# ОДИН СЕРЫЙ НА ВСЮ МАШИНУ (Эльдар, 02.11.2026: «подтяни по цветам детали друг с другом,
# там баланс белого скачет — серый разный везде, а должен быть единым»). Так и есть,
# промерено по металлу (средний цвет непрозрачных точек яркостью 90…245 и насыщенностью
# меньше 60, то есть без красных накладок и без пересветов):
#     стеллаж, стойки и верхняя рейка   R/G 1.005   B/G 1.012   — чистый серый
#     балка Champagne aluminum          R/G 1.066   B/G 0.944   — тёплая
#     ось Vertical Gantry               R/G 1.049   B/G 0.955   — тёплая
#     брус Precision                    R/G 1.023   B/G 0.985
#     колонна Dental motion             R/G 1.054   B/G 0.956
# Эталон — стеллаж: он занимает почти всю машину, на нём держатся все замеры, и красный
# баннер с заготовками сняты в его свете. Подвижные детали приводятся к его балансу: по
# каналу R и B берётся множитель, который переводит измеренное отношение в эталонное,
# канал G не трогается — значит яркость детали остаётся прежней, меняется только оттенок.
# Отношения выше — для глаза, по байтам sRGB; СЧИТАЕТСЯ поправка в линейном свете: и
# промер, и множитель, и эталон. Если взять множитель по sRGB-отношению, а положить его в
# линейный свет, поправка выходит втрое слабее нужной (0.9427 в линейном — это всего 0.974
# по байту), и тёплый оттенок остаётся. Канал G не трогается — значит яркость детали
# остаётся прежней, меняется только оттенок.
# Поправка общая на весь файл, как и положено балансу белого, — красные накладки деталей
# после неё садятся на красный баннер стеллажа, а не спорят с ним.
from PIL import Image
import numpy as np
import os
SRC = 'src/pictures/Expo timeline artefacts'
DST = 'assets/photo'
REF_BOX = (106, 300, 154, 900)   # левая стойка стеллажа — эталонный металл
JOBS = [
    # (файл исходника, окно x0,y0,x1,y1, scale, имя ассета, окно промера металла или None)
    ('Industrial Rack with Modular Chambers and Trays.png', (86, 24, 1451, 1003), 1.0, 'r_bzf_frame2', None),
    ('Champagne aluminum gantry beam.png',                  (16, 152, 2154, 571), 0.5, 'r_bzf_beam2', (600, 290, 1500, 440)),
    ('Vertical Gantry Guide Column.png',                    (361, 14, 552, 1754), 0.5, 'r_bzf_axis2', (404, 600, 466, 1400)),
    ('Champagne-white precision gantry beam.png',           (16, 274, 2156, 446), 0.5, 'r_bzf_beam3', (600, 290, 1500, 430)),
    ('Champagne-white dental motion column.png',            (255, 19, 469, 2155), 0.5, 'r_bzf_axis3', (264, 600, 460, 1400)),
]


def srgb2lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def metal(a, box):
    """средний цвет металла в окне, в линейном свете: без прозрачного, без красного,
       без пересветов (они упёрты в 255 и отношение каналов на них врёт)"""
    x0, y0, x1, y1 = box
    s = a[y0:y1, x0:x1].astype(float)
    p = s[s[..., 3] > 200][:, :3]
    lum = p.mean(1)
    sel = (lum > 90) & (lum < 245) & ((p.max(1) - p.min(1)) < 60)
    return srgb2lin(p[sel] / 255.0).mean(0)


def balance(im, gain):
    """множители по каналам — в линейном свете, альфа не трогается"""
    a = np.array(im).astype(np.float64) / 255.0
    lin = srgb2lin(a)
    for c in (0, 2):
        lin[..., c] *= gain[c]
    lin = np.clip(lin, 0, 1)
    out = np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)
    out[..., 3] = a[..., 3]
    return Image.fromarray(np.round(out * 255).astype(np.uint8))


rr, rg, rb = metal(np.array(Image.open(os.path.join(SRC, JOBS[0][0])).convert('RGBA')), REF_BOX)
REF = (rr / rg, rb / rg)
print('эталон — металл стеллажа, в линейном свете: R/G %.4f  B/G %.4f' % REF)
for fn, box, sc, name, mbox in JOBS:
    im = Image.open(os.path.join(SRC, fn)).convert('RGBA')
    note = 'эталон'
    if mbox:
        r, g, b = metal(np.array(im), mbox)
        gain = (REF[0] / (r / g), 1.0, REF[1] / (b / g))
        im = balance(im, gain)
        note = 'R ×%.4f  B ×%.4f  (было R/G %.4f  B/G %.4f)' % (gain[0], gain[2], r / g, b / g)
    im = im.crop(box)
    if sc != 1.0:
        im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    im.save(os.path.join(DST, name + '.png'))
    im.save(os.path.join(DST, name + '.webp'), quality=92, method=6)
    print('%-14s %4d x %4d  %s' % (name, im.width, im.height, note))
