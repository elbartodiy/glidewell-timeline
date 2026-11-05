# ТРИ РЕНДЕРА ДЛЯ УДАРА КУВАЛДОЙ НА 2009-м (Эльдар, 04.11.2026).
#
# 1) «PFM and Zirconia Molar Crowns Cutaway» — две коронки в одном кадре, с
#    одинаковым вырезом: слева металлокерамика (видно серый колпачок и слои
#    фарфора), справа цельный цирконий. Сняты одним кадром нарочно, чтобы
#    совпали по свету и размеру, поэтому режутся ОДНОЙ вертикальной рамкой —
#    иначе подошвы встанут на разной высоте.
#    Замерено: предметы занимают колонки 56…857 и 915…1718 (ширина 802 и 804,
#    зазор 58), строки 83…807.
# 2) «Weathered Sledgehammer» — кувалда бойком вниз, рукоять уходит вверх.
# 3) «Shattered Dental Crown Debris Pile» — осколки металлокерамики после удара.
#
# Все три уже с альфой: только обрезаем, без масштабирования и без вмешательства
# в сам рендер. Альфу ниже 14 обнуляем — у генератора по кромке остаётся
# цветная пыль, которая на светлом полу зала читается как грязь.
from PIL import Image
import numpy as np
import os

SRC = 'src/pictures/Expo timeline artefacts'
DST = 'assets/photo'

def clean(im):
    a = np.array(im)
    a[:, :, 3] = np.where(a[:, :, 3] < 14, 0, a[:, :, 3])
    return Image.fromarray(a)

def box_of(im, thr=110):
    al = np.array(im)[:, :, 3]
    xs = np.where((al > thr).sum(0) > 3)[0]
    ys = np.where((al > thr).sum(1) > 3)[0]
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1

def save(im, name):
    im.save(os.path.join(DST, name + '.png'))
    im.save(os.path.join(DST, name + '.webp'), quality=94, method=6)
    print('%-18s %d x %d' % (name, im.width, im.height))

# --- две коронки: своя рамка по горизонтали, ОБЩАЯ по вертикали
pair = clean(Image.open(os.path.join(SRC, 'PFM and Zirconia Molar Crowns Cutaway.png')).convert('RGBA'))
al = np.array(pair)[:, :, 3]
cols = (al > 110).sum(0)
runs, inr = [], False
for i, v in enumerate(cols):
    if v > 3 and not inr:
        s = i; inr = True
    elif v <= 3 and inr:
        runs.append((s, i - 1)); inr = False
if inr:
    runs.append((s, len(cols) - 1))
runs = [r for r in runs if r[1] - r[0] > 30]
assert len(runs) == 2, runs
ys = np.where((al > 110).sum(1) > 3)[0]
y0, y1 = int(ys.min()), int(ys.max()) + 1
for (x0, x1), name in zip(runs, ['r_bz_pfm', 'r_bz_zir']):
    save(pair.crop((x0, y0, x1 + 1, y1)), name)

# --- кувалда и осколки: по своей рамке
for f, name in [('Weathered Sledgehammer Isolated on Transparent Background.png', 'r_bz_hammer'),
                ('Shattered Dental Crown Debris Pile.png', 'r_bz_shards')]:
    im = clean(Image.open(os.path.join(SRC, f)).convert('RGBA'))
    save(im.crop(box_of(im)), name)
