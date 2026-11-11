"""تعديل سطر نص الشرح في صفحة 4K، وإخراج نسخة 1080 منها للمحرك."""
import sys, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt
S = bt.S
BGP = np.array([234, 239, 242], np.float32)          # خلفية الصفحة (BGR)


def page_src(n):
    import os
    p = f'{S}/hr/pages4k_edit/{n:03d}.png'
    return cv2.imread(p if os.path.exists(p) else f'{S}/hr/pages4k/{n:03d}.png')


def ink_color(img):
    f = img.astype(np.float32); L = f.mean(2); m = L < 60
    return np.median(f[m].reshape(-1, 3), 0)


def replace_line(n, base, ah, new, x0=300, x1=3540, up=1.25, down=0.6, center=None):
    """يمحو مكوّنات السطر (خط قاعدته base) ويضع new=(alpha, b) متوسطاً على مركز السطر القديم."""
    img = page_src(n).astype(np.float32)
    a = bt.alpha(img.astype(np.uint8))
    y0, y1 = int(base - 1.8 * ah), int(base + 1.0 * ah)
    sub = a[y0:y1, x0:x1]
    nl, lab, st, cen = cv2.connectedComponentsWithStats((sub > 0.2).astype(np.uint8), 8)
    lo, hi = base - up * ah, base + down * ah
    kill = np.zeros(sub.shape, bool)
    for j in range(1, nl):
        if lo <= cen[j][1] + y0 <= hi: kill |= lab == j
    ys, xs = np.nonzero(kill)
    oc = (xs.min() + xs.max()) / 2 + x0 if center is None else center
    kill = cv2.dilate(kill.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    reg = img[y0:y1, x0:x1]; reg[kill] = BGP
    col = ink_color(page_src(n))
    na, nb = new
    h, w = na.shape
    X0 = int(round(oc - w / 2)); Y0 = int(round(base - nb))
    r = img[Y0:Y0 + h, X0:X0 + w]; al = na[..., None]
    r[:] = r * (1 - al) + col * al
    out = np.clip(img + 0.5, 0, 255).astype(np.uint8)
    return out, dict(old_x=(int(xs.min() + x0), int(xs.max() + x0)), new_x=(X0, X0 + w), center=oc)


def save(n, img4k):
    cv2.imwrite(f'{S}/hr/pages4k_edit/{n:03d}.png', img4k)
    small = cv2.resize(img4k[:2159], (1920, 1079), interpolation=cv2.INTER_AREA)
    cv2.imwrite(f'{S}/pages_edit/{n:03d}.png', small)


def kill_line(n, base, ah, x0=300, x1=3540, up=1.25, down=0.6):
    """يمحو سطراً كاملاً (مكوّناته في نطاق خط قاعدته)."""
    img = page_src(n).astype(np.float32)
    a = bt.alpha(img.astype(np.uint8))
    y0, y1 = int(base - 1.8 * ah), int(base + 1.0 * ah)
    sub = a[y0:y1, x0:x1]
    nl, lab, st, cen = cv2.connectedComponentsWithStats((sub > 0.2).astype(np.uint8), 8)
    kill = np.zeros(sub.shape, bool)
    for j in range(1, nl):
        if base - up * ah <= cen[j][1] + y0 <= base + down * ah: kill |= lab == j
    kill = cv2.dilate(kill.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    reg = img[y0:y1, x0:x1]; reg[kill] = BGP
    return np.clip(img + 0.5, 0, 255).astype(np.uint8)
