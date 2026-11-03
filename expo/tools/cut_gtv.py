# Логотип Glidewell TV для стойки GTV в зале (Эльдар, 03.11.2026: «надо поставить
# логотип, который можно найти по ссылке и здесь»).
#
# ОТКУДА ЗНАК. На glidewelldental.com/company/tv вектора нет: логотип там живёт
# только внутри видео и в мелких растрах (gtv-icons-*.png — 225x110 на всю пару
# иконок). Тот же знак в чистом виде отдаёт App Store — иконка приложения
# Glidewell TV (Connected Television Group) в 1024x1024 PNG:
#   https://itunes.apple.com/search?term=glidewell+tv&entity=software → artworkUrl512
#   → .../AppIcon-0-0-1x_U007epad-0-1-85-220.png/1024x1024bb.png
# Он совпадает со знаком на самой стойке (фото IMG_6398) и на табличке с QR.
#
# ВЫРЕЗКА. Знак нарисован красным по белому, без альфы. Белое выбивается в
# прозрачность по МИНИМАЛЬНОМУ каналу: у белого он 255, у фирменного красного
# около 30, у маронового подбоя буквы V — около 20. Порог 60 даёт край в один
# пиксель исходника, а цвет под ним восстанавливается развёрткой композиции
# по белому (C = (Csrc − (1−A)·255) / A) — иначе кромка знака светлеет и на
# панели вокруг букв появляется белый ореол.
from PIL import Image
import numpy as np, os
SRC = 'src/pictures/Logo/gtv_appicon_1024.png'
DST = 'assets/photo'
im = Image.open(SRC).convert('RGB')
a = np.asarray(im).astype(np.float64)
mn = a.min(axis=2)
A = np.clip((255.0 - mn) / (255.0 - 60.0), 0.0, 1.0)
out = np.zeros(a.shape[:2] + (4,), np.float64)
safe = np.maximum(A, 1e-3)[..., None]
out[..., :3] = np.clip((a - (1.0 - A[..., None]) * 255.0) / safe, 0, 255)
out[..., 3] = A * 255.0
img = Image.fromarray(np.round(out).astype(np.uint8), 'RGBA')
img = img.crop(img.getbbox())          # по альфе: только сам знак
img.save(os.path.join(DST, 'r_gtv_logo.png'))
img.save(os.path.join(DST, 'r_gtv_logo.webp'), quality=94, method=6)
print('r_gtv_logo %d x %d' % img.size)
