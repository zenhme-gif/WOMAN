"""خط العناوين والمربعات (الدرس الرابع): ألفا النص الأبيض في اللافتة الحمراء، والرمادي داخل المربع الأبيض."""
import cv2, numpy as np
import bt
from scipy import ndimage as ndi


def banner_hull(img):
    f = img.astype(int); red = (f[..., 2] - f[..., 1] > 60) & (f[..., 2] - f[..., 0] > 60)
    red[1000:] = False
    h = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8)) > 0
    h = ndi.binary_fill_holes(h)
    n, lab, st, _ = cv2.connectedComponentsWithStats(h.astype(np.uint8))
    return lab == 1 + int(np.argmax(st[1:, 4])) if n > 1 else h


def alpha_t(n, x0, x1, y0, y1):
    """ألفا نص العنوان: أبيض داخل اللافتة، أو رمادي (64) على أبيض داخل المربع."""
    img = bt.page(n); reg = img[y0:y1, x0:x1].astype(np.float32)
    mn = reg.min(2); sat = reg.max(2) - reg.min(2)
    if y0 < 950:
        hull = banner_hull(img)[y0:y1, x0:x1]
        hull = cv2.erode(hull.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        a = np.clip((mn - 94) / (255 - 94), 0, 1); a[~hull] = 0
    else:
        a = np.clip((250 - reg.mean(2)) / (250 - 64), 0, 1); a[sat > 45] = 0
    return a.astype(np.float32)


def comps(n, x0, x1, y0, y1):
    a = alpha_t(n, x0, x1, y0, y1)
    nl, lab, st, c = cv2.connectedComponentsWithStats((a > 0.35).astype(np.uint8), 8)
    return a, nl, lab, st, c


def T(n, x0, x1, y0, y1, base, cxa=-1e9, cxb=1e9, up=1.6, down=0.7, ah=105):
    """قطعة بخط العناوين: (ألفا، خط القاعدة داخلها)."""
    a, nl, lab, st, c = comps(n, x0, x1, y0, y1)
    keep = np.zeros(a.shape, bool)
    for j in range(1, nl):
        cx, cy = c[j][0] + x0, c[j][1] + y0
        if cxa <= cx <= cxb and base - up * ah <= cy <= base + down * ah: keep |= lab == j
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    return np.where(keep, a, 0).astype(np.float32), float(base - y0)


def tbase(n, x0, x1, y0, y1):
    """خط القاعدة: أسفل الألفات (مكوّنات طويلة رفيعة) بخط العناوين."""
    a, nl, lab, st, c = comps(n, x0, x1, y0, y1)
    hs = [st[j, 3] for j in range(1, nl)]
    if not hs: return None
    mh = np.percentile(hs, 90)
    bots = [st[j, 1] + st[j, 3] for j in range(1, nl) if st[j, 3] > 2.5 * st[j, 2] and st[j, 3] > 0.6 * mh]
    return y0 + float(np.median(bots)) if bots else None


def show(n, x0, x1, y0, y1, path, sc=1.0, step=10):
    a = alpha_t(n, x0, x1, y0, y1)
    im = cv2.cvtColor((255 - a * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
    for x in range(0, x1 - x0):
        if (x0 + x) % step == 0:
            big = (x0 + x) % (step * 5) == 0
            cv2.line(im, (int(x * sc), 0), (int(x * sc), 18 if big else 7), (0, 0, 255), 1)
            if big: cv2.putText(im, str(x0 + x), (int(x * sc) + 2, 30), 0, 0.45, (0, 0, 255), 1)
    for y in range(0, y1 - y0):
        if (y0 + y) % step == 0:
            big = (y0 + y) % (step * 5) == 0
            cv2.line(im, (0, int(y * sc)), (18 if big else 7, int(y * sc)), (255, 0, 0), 1)
            if big: cv2.putText(im, str(y0 + y), (20, int(y * sc) + 4), 0, 0.45, (255, 0, 0), 1)
    cv2.imwrite(path, im)


def sbase(n, x0, x1, y0, y1):
    """خط القاعدة من الوصلات الأفقية الخالصة: أسفل الوصلة + 3 (كما في اللافتات: ألف 620، أسفل الوصلة 617)."""
    a = alpha_t(n, x0, x1, y0, y1) > 0.4
    col = a.sum(0); bots = []
    for i in range(a.shape[1]):
        if 20 <= col[i] <= 32:
            ys = np.nonzero(a[:, i])[0]
            if ys.max() - ys.min() + 1 == col[i]: bots.append(ys.max())
    return y0 + float(np.median(bots)) + 3 if bots else None
