"""الدرس الثالث، ص116: إضافة الإحالة «[الماعون: ٤–٥]» بعد الآية، بخط أميري، وتوسيط السطر كله."""
import sys, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
from PIL import Image, ImageDraw, ImageFont
import bt, edit
S = bt.S
FONT = f'{S}/fonts_dl/amiri_latin/amiri-merged-400.ttf'      # أميري العادي (عربي + لاتيني للأقواس والنقطتين والشرطة)
SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 84
GAP = 50
BASE = 1907                                                    # قاعدة سطر الآية في صفحة 4K
TXT = '[الماعون: ٤–٥]'

img = edit.page_src(116)
f = img.astype(np.float32)
a = bt.alpha(img)
y0, y1, x0, x1 = 1745, 2010, 300, 3540
sub = a[y0:y1, x0:x1]
nl, lab, st, cen = cv2.connectedComponentsWithStats((sub > 0.2).astype(np.uint8), 8)
m = np.zeros(sub.shape, bool)
for j in range(1, nl):
    if cen[j][1] + y0 >= 1750: m |= lab == j
ys, xs = np.nonzero(m)
ax0, ax1 = xs.min() + x0, xs.max() + x0
print('ayah x', ax0, ax1, 'y', ys.min() + y0, ys.max() + y0)
mk = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
ay_al = np.where(mk, sub, 0).astype(np.float32)
L = f[y0:y1, x0:x1].mean(2)
col = np.median(f[y0:y1, x0:x1][m & (L < 60)].reshape(-1, 3), 0)
print('ayah ink colour', col)

# الإحالة
fo = ImageFont.truetype(FONT, SIZE)
W, H = 1400, 300
im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
d.text((W - 20, 200), TXT, font=fo, fill=255, anchor='rs', direction='rtl', language='ar')
ra = np.array(im).astype(np.float32) / 255
cy, cx = np.nonzero(ra > 0.02)
ra = ra[:, cx.min():cx.max() + 1]; rb = 200            # قاعدة الإحالة داخل مصفوفتها
rw = ra.shape[1]
aw = ax1 - ax0 + 1
total = rw + GAP + aw
nx1 = int(round(1920 + total / 2))                      # الحافة اليمنى للسطر الجديد
dx = nx1 - ax1
rx0 = nx1 - total + 1                                   # بداية الإحالة (يسار السطر)
print('ref w', rw, 'shift ayah by', dx, 'line', rx0, nx1)

# امحُ الآية القديمة ثم ارسمها مزاحة، ثم الإحالة
kill = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
reg = f[y0:y1, x0:x1]; reg[kill] = edit.BGP
layer = np.zeros(a.shape, np.float32)
layer[y0:y1, x0 + dx:x1 + dx] = np.maximum(layer[y0:y1, x0 + dx:x1 + dx], ay_al)
Y0 = BASE - rb
layer[Y0:Y0 + H, rx0:rx0 + rw] = np.maximum(layer[Y0:Y0 + H, rx0:rx0 + rw], ra)
al = layer[..., None]
f = f * (1 - al) + col * al
out = np.clip(f + 0.5, 0, 255).astype(np.uint8)
if '--save' in sys.argv:
    edit.save(116, out); print('saved')
cv2.imwrite(f'{S}/txt/e7.png', out[1350:2050, 300:3540])
cv2.imwrite(f'{S}/txt/e7_small.jpg', cv2.resize(out, None, fx=0.3, fy=0.3))
