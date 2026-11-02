"""لوح الخلفية بدقة 3840×2160: الزخارف مكبّرة بحواف حادة، والشعارات من مصادرها العالية الدقة
(شعار «فقه المرأة المسلمة» واسم الشيخ من صفحة الغلاف الأصلية، وشعار الجمعية من ملفها الرسمي)،
وموضع كل شعار ومقاسه بمطابقة اللوح الأصلي."""
import cv2, numpy as np, glob, sys
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
sys.path.insert(0, f'{S}/hr')
from sharpup import sharp_up
BG = np.array([228, 236, 240], np.float32)
p = cv2.imread(f'{S}/l2/plate.png')
P4c = cv2.resize(p, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
out = sharp_up(cv2.GaussianBlur(p, (0, 0), 0.5), k=2.0).astype(np.float32)
g = lambda x: cv2.cvtColor(np.clip(x, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)


def fit(img, region, scales):
    tx0, ty0, tx1, ty1 = region; T = g(P4c[ty0:ty1, tx0:tx1]); best = None
    for s in scales:
        r = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        if r.shape[0] >= T.shape[0] or r.shape[1] >= T.shape[1]: continue
        m = cv2.matchTemplate(T, g(r), cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(m)
        if best is None or mx > best[0]: best = (mx, s, loc[0] + tx0, loc[1] + ty0)
    return best


def paste(img, alpha, x, y):
    h, w = alpha.shape
    reg = out[y:y + h, x:x + w]
    reg[:] = img.astype(np.float32) * alpha[..., None] + reg * (1 - alpha[..., None])


# 1) تفريغ مواضع الشعارات في اللوح المكبَّر (دون الفاصل الذهبي والنقاط الثلاث)
for x0, y0, x1, y1 in [(436, 120, 764, 336), (2810, 130, 3080, 330), (3120, 130, 3600, 330)]:
    out[y0:y1, x0:x1] = BG
# 2) شعار «فقه المرأة المسلمة» والسطران تحت الغلاف
A = cv2.imread(glob.glob(f'{S}/rar_src/*/*Page_001.png')[0])
PBG = np.median(A[:200, 4000:8000].reshape(-1, 3), 0).astype(np.float32)
for name, (x0, y0, x1, y1), reg in [('logo', (1340, 198, 2500, 950), (400, 100, 800, 370)),
                                    ('fadila', (1546, 1306, 2293, 1555), (3100, 110, 3640, 260)),
                                    ('name', (1148, 1624, 2692, 1988), (3100, 170, 3640, 360))]:
    crop = A[y0 * 4:y1 * 4, x0 * 4:x1 * 4]
    sc = fit(crop, reg, np.arange(0.06, 0.072, 0.0005)) if name != 'logo' else fit(crop, reg, np.arange(0.062, 0.069, 0.00025))
    mx, s, x, y = sc
    r = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
    a = np.clip(np.abs(r - PBG).max(2) / 60.0, 0, 1)
    paste(r + (BG - PBG) * (1 - a[..., None]), np.clip(np.abs(r - PBG).max(2) / 6.0, 0, 1), x, y)
    print(name, 'score %.3f scale %.4f at' % (mx, s), x, y, r.shape[1], r.shape[0], flush=True)
# 3) شعار الجمعية: الرمز والكلمتان «جمعية هداة» من الملف الرسمي
H = cv2.imread(f'{S}/hr/hdat_big.png', cv2.IMREAD_UNCHANGED).astype(np.float32)
for name, (y0, y1, x0, x1), reg in [('hdat-icon', (17, 1035, 0, 2548), (2780, 110, 3100, 300)),
                                    ('hdat-text', (1115, 1352, 1000, 2548), (2780, 220, 3100, 340))]:
    piece = H[y0:y1, x0:x1]; al = piece[..., 3:] / 255.0
    flat = piece[..., :3] * al + BG * (1 - al)
    mx, s, x, y = fit(flat, reg, np.arange(0.05, 0.16, 0.001))
    s2 = s
    r = cv2.resize(piece, None, fx=s2, fy=s2, interpolation=cv2.INTER_AREA)
    paste(r[..., :3], r[..., 3] / 255.0, x, y)
    print(name, 'score %.3f scale %.4f at' % (mx, s), x, y, r.shape[1], r.shape[0], flush=True)
plate = np.clip(out + 0.5, 0, 255).astype(np.uint8)
cv2.imwrite(f'{S}/hr/plate4k.png', plate)
small = cv2.resize(plate, (1920, 1080), interpolation=cv2.INTER_AREA).astype(int)
d = np.abs(small - p.astype(int)).max(2)
print('downscaled vs original plate: mean %.2f, >30 px %d' % (d.mean(), (d > 30).sum()))
cv2.imwrite(f'{S}/hr/plate4k_view.png', np.vstack([np.hstack([plate[100:360, 380:800], P4c[100:360, 380:800]]),
                                                  np.hstack([plate[100:360, 2780:3200], P4c[100:360, 2780:3200]]),
                                                  np.hstack([plate[100:360, 3200:3620], P4c[100:360, 3200:3620]])]))
