# Знак fastscan.io — вместо набранного имени на бухте 2022 и на её странице
# (Эльдар, 05.11.2026: «fastscan.io на 2022 у тебя есть — нужно найти этот
# логотип и поставить логотип вместо просто текста внизу там»; файл он положил
# 06.11.2026 в ~/Work/00. Assets/Logo etc).
#
# Файл уже с альфой — только обрезаем по ней, ничего не масштабируя и не
# перерисовывая: 400 × 225 с полем, содержимое 398 × 50. Буквы серые, точка и
# точка над i — красные; тот же набор, что у glidewell.io.
#
# Базовая линия: у «fastscan.io» нет выносных вниз, поэтому низ обрезанного
# знака И ЕСТЬ базовая линия (замер по альфе: буквы занимают строки 0…49 из 50,
# ™ кончается на 48). Отсюда base = 1.0 в TITLE_LOGOS — против 221/267 у
# glidewell.io, где вниз уходит «g».
from PIL import Image
import numpy as np
import os

SRC = os.path.expanduser('~/Work/00. Assets/Logo etc/fastscan-io-logo.png')
DST = 'assets/photo'

im = Image.open(SRC).convert('RGBA')
al = np.array(im)[:, :, 3]
xs = np.where((al > 16).any(0))[0]
ys = np.where((al > 16).any(1))[0]
box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
out = im.crop(box)
out.save(os.path.join(DST, 'fastscan_io.png'))
out.save(os.path.join(DST, 'fastscan_io.webp'), quality=95, method=6)
print('fastscan_io  %d x %d  из окна %s' % (out.width, out.height, box))

# ВЫВОРОТКА — для тёмного листа страницы года: серые буквы и ™ в белый, красные
# точки как есть (тот же приём, что у glidewell_io_rev). Альфа не трогается,
# поэтому сглаживание краёв сохраняется.
a = np.array(out).astype(int)
r, g, b, al = a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3]
red = (r - np.maximum(g, b)) > 40          # красная точка и точка над i
out2 = a.copy()
out2[~red, 0] = 255; out2[~red, 1] = 255; out2[~red, 2] = 255
rev = Image.fromarray(out2.astype('uint8'))
rev.save(os.path.join(DST, 'fastscan_io_rev.png'))
rev.save(os.path.join(DST, 'fastscan_io_rev.webp'), quality=95, method=6)
print('fastscan_io_rev  %d x %d  (красных пикселей %d)' % (rev.width, rev.height, int(red.sum())))
