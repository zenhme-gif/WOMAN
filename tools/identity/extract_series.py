"""عناصر سلسلة «فقه المرأة المسلمة» من صفحة الغلاف الأصلية (15364×8636) بخلفية شفافة.
الألوان مسطّحة على خلفية مسطّحة #F2EFEA: لكل بكسل أقرب لون حبر، والألفا = بُعده عن الخلفية نسبةً إلى بُعد الحبر."""
import cv2, numpy as np, sys
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
R = f'{S}/rar_src/cf43f75c-_______'
P = lambda n: cv2.imread(f'{R}/خرائط فقه المرأة المسلمة_الطهارة والصلاة 1920×1080 دون خلفية_Page_{n:03d}.png')
BG = np.array([234, 239, 242], np.float32)                                   # BGR لـ #F2EFEA
INKS = np.array([[145, 86, 25], [117, 116, 219], [72, 197, 228]], np.float32)  # #195691 #DB7475 #E4C548 (BGR)


def cutout(img, pad=40):
    f = img.astype(np.float32)
    d = f - BG
    dirs = INKS - BG
    # إسقاط على كل لون حبر، واختيار الأقرب
    best_a = np.zeros(f.shape[:2], np.float32); best_k = np.zeros(f.shape[:2], np.int32); best_e = np.full(f.shape[:2], 1e9, np.float32)
    for k, v in enumerate(dirs):
        a = np.clip((d @ v) / (v @ v), 0, 1)
        e = np.linalg.norm(d - a[..., None] * v, axis=2)
        m = e < best_e
        best_a[m] = a[m]; best_k[m] = k; best_e[m] = e[m]
    ys, xs = np.nonzero(best_a > 0.05)
    y0, y1, x0, x1 = max(0, ys.min() - pad), min(f.shape[0], ys.max() + pad), max(0, xs.min() - pad), min(f.shape[1], xs.max() + pad)
    col = INKS[best_k[y0:y1, x0:x1]]
    out = np.dstack([col, best_a[y0:y1, x0:x1] * 255]).astype(np.float32)
    return np.clip(out + 0.5, 0, 255).astype(np.uint8), (x0, y0, x1, y1), float(best_e[best_a > 0.5].mean())


if __name__ == '__main__':
    p1 = P(1)
    jobs = {'series-logo': (800, 3800, 5300, 10100), 'three-dots': (4250, 4700, 7000, 8400), 'sheikh-name': (4750, 8400, 4000, 11500),
            'pattern-border': (0, 8636, 0, 1250)}
    for name, (y0, y1, x0, x1) in jobs.items():
        out, bb, err = cutout(p1[y0:y1, x0:x1])
        b = (bb[0] + x0, bb[1] + y0, bb[2] + x0, bb[3] + y0)
        # تحذير القصّ: الحبر لا يلامس حدود نافذة البحث
        a = out[..., 3] > 12
        touch = [a[0].any() and bb[1] == 0, a[-1].any() and bb[3] == y1 - y0, a[:, 0].any() and bb[0] == 0, a[:, -1].any() and bb[2] == x1 - x0]
        cv2.imwrite(f'{S}/kit/series/{name}.png', out)
        print(name, 'bbox in page', b, 'size', out.shape[1], 'x', out.shape[0], 'mean residual', round(err, 2), 'touches window edge', touch)
