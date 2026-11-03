# Нарезка новых деталей фабрики BruxZir (Эльдар, 02.11.2026: «я тут обновил детали»).
# Каждая деталь режется по своему окну в точках исходника и уменьшается в scale раз —
# ровно так же, как резались r_bzf_* 29.10.2026.
from PIL import Image
import os
SRC = 'src/pictures/Expo timeline artefacts'
DST = 'assets/photo'
JOBS = [
    # (файл исходника, окно x0,y0,x1,y1, scale, имя ассета)
    ('Industrial Rack with Modular Chambers and Trays.png', (86, 24, 1451, 1003), 1.0, 'r_bzf_frame2'),
    ('Champagne aluminum gantry beam.png',                  (16, 152, 2154, 571), 0.5, 'r_bzf_beam2'),
    ('Vertical Gantry Guide Column.png',                    (361, 14, 552, 1754), 0.5, 'r_bzf_axis2'),
    ('Champagne-white precision gantry beam.png',           (16, 274, 2156, 446), 0.5, 'r_bzf_beam3'),
    ('Champagne-white dental motion column.png',            (255, 19, 469, 2155), 0.5, 'r_bzf_axis3'),
]
for fn, box, sc, name in JOBS:
    im = Image.open(os.path.join(SRC, fn)).convert('RGBA').crop(box)
    if sc != 1.0:
        im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
    im.save(os.path.join(DST, name + '.png'))
    im.save(os.path.join(DST, name + '.webp'), quality=92, method=6)
    print('%-16s %4d x %4d  из %s' % (name, im.width, im.height, fn[:40]))
