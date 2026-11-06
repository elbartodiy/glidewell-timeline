# Подпись Джима — для белой таблички перед горой книг (Эльдар, 05.11.2026:
# «перед книгами должна стоять табличка „Don't forget to sign a book“, и там
# подпись Джима; белая, соответственно, табличка»). Файл он положил в артефакты.
#
# Файл уже с альфой и чистый: только обрезаем по ней. 1776 × 886 с полем,
# содержимое 1719 × 732. Чернила не трогаем — на табличке они рисуются как
# есть, тёмным по белому.
from PIL import Image
import numpy as np
import os

SRC = 'src/pictures/Expo timeline artefacts/James R. Glidewell Signature and Date.png'
DST = 'assets/photo'

im = Image.open(SRC).convert('RGBA')
al = np.array(im)[:, :, 3]
xs = np.where((al > 16).any(0))[0]
ys = np.where((al > 16).any(1))[0]
box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
out = im.crop(box)
out.save(os.path.join(DST, 'jim_sign.png'))
out.save(os.path.join(DST, 'jim_sign.webp'), quality=92, method=6)
print('jim_sign  %d x %d  из окна %s' % (out.width, out.height, box))
