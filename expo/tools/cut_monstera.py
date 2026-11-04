# Монстера в стеклянной вазе — на прилавок перед табло TODAY (Эльдар, 04.11.2026:
# «Variegated Snake Plant and Monstera Duo в артефактах — возьми цветок справа и
# поставь его вместо тетрадок, которые лежат на столе»).
#
# В исходнике два растения: сансевиерия в латунном кашпо (колонки 480…677) и
# монстера в синей вазе (1128…1850) — между ними сплошной разрыв по альфе,
# поэтому правое берётся просто правее разрыва. Файл уже с альфой, фон резать
# не надо: обрезаем по её bbox и сохраняем как есть, без масштабирования —
# 723 × 685 это ровно тот размер, при котором зал ещё уменьшает его мипами.
from PIL import Image
import numpy as np
import os

SRC = 'src/pictures/Expo timeline artefacts/Variegated Snake Plant and Monstera Duo.png'
DST = 'assets/photo'
SPLIT = 900          # любая колонка внутри разрыва 677…1128

im = Image.open(SRC).convert('RGBA')
a = np.array(im)
right = a[:, SPLIT:, :]
al = right[:, :, 3]
xs = np.where((al > 16).any(0))[0]
ys = np.where((al > 16).any(1))[0]
box = (SPLIT + int(xs.min()), int(ys.min()), SPLIT + int(xs.max()) + 1, int(ys.max()) + 1)
out = im.crop(box)
out.save(os.path.join(DST, 'r_monstera.png'))
out.save(os.path.join(DST, 'r_monstera.webp'), quality=92, method=6)
print('r_monstera  %d x %d  из окна %s' % (out.width, out.height, box))
