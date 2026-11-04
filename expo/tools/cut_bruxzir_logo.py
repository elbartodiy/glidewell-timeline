# Глянцевая вывеска BruxZir® на стену 2009-го (Эльдар, 04.11.2026: «Glossy Blue
# BruxZir® Logo в артефактах — замени старую табличку "коминг сун" на новую»,
# «только не так криво на этот раз», «ровно под годом»).
#
# Файл уже с альфой: только обрезаем по ней, без масштабирования и без
# вмешательства в сам рендер. Прежний щит (bruxzir_soon.png) остаётся в
# assets — он больше не рисуется, но и не удалён.
from PIL import Image
import numpy as np
import os

SRC = 'src/pictures/Expo timeline artefacts/Glossy Blue BruxZir® Logo.png'
DST = 'assets/photo'

im = Image.open(SRC).convert('RGBA')
al = np.array(im)[:, :, 3]
xs = np.where((al > 16).any(0))[0]
ys = np.where((al > 16).any(1))[0]
box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
out = im.crop(box)
out.save(os.path.join(DST, 'r_bruxzir_logo.png'))
out.save(os.path.join(DST, 'r_bruxzir_logo.webp'), quality=92, method=6)
print('r_bruxzir_logo  %d x %d  из окна %s' % (out.width, out.height, box))
