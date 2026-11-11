import sys, pickle, cv2, numpy as np, os
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt, tf, edit
S = bt.S
D = pickle.load(open(f'{S}/txt/l4title.pkl', 'rb'))


def paste(img, piece, cx, base, color):
    a, b = piece; h, w = a.shape
    X0 = int(round(cx - w / 2)); Y0 = int(round(base - b))
    r = img[Y0:Y0 + h, X0:X0 + w]; al = a[..., None]
    r[:] = r * (1 - al) + np.array(color, np.float32) * al


def set_title(img, piece):
    f = img.astype(int); hull = tf.banner_hull(img.astype(np.uint8))
    inner = cv2.erode(hull.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
    mn = f.min(2)
    red = np.median(img[hull & (mn < 100)].reshape(-1, 3), 0)
    txt = inner & (mn > 105)
    ys, xs = np.nonzero(txt & (mn > 200))
    cx = (xs.min() + xs.max()) / 2
    white = np.median(img[txt & (mn > 240)].reshape(-1, 3), 0)
    k = cv2.dilate(txt.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    k &= inner
    img[k] = red
    paste(img, piece, cx, 619, white)
    return dict(cx=cx, red=red.tolist(), white=white.tolist())


def set_box(img, lines, bases):
    reg = img[960:1335, 1262:2578]
    L = reg.mean(2); sat = reg.max(2) - reg.min(2)
    txt = (L < 245) & (sat < 45)
    ys, xs = np.nonzero(txt & (L < 150))
    cx = 1262 + (xs.min() + xs.max()) / 2
    k = cv2.dilate(txt.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    k &= ~(cv2.dilate((sat >= 45).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)   # لا يُمس الإطار الأزرق ولا التظليل
    reg[k] = 255
    col = (64, 64, 64)
    for pc, b in zip(lines, bases): paste(img, pc, 1919.0, b, col)
    return dict(old_cx=cx)


jobs = {122: ('HUKM', [1181]), 123: ('ILLA', [1181]), 136: ('136', [1093, 1269]), 137: ('137', [1093, 1269])}
for n, (key, bases) in jobs.items():
    for p in (f'{S}/hr/pages4k_edit/{n:03d}.png', f'{S}/pages_edit/{n:03d}.png'):
        if os.path.exists(p): os.remove(p)
    img = edit.page_src(n).astype(np.float32)
    info = {}
    if n in (122, 123): info['title'] = set_title(img, D['TITLE'])
    lines = {'HUKM': [D['BOX_HUKM']], 'ILLA': [D['BOX_ILLA']], '136': D['BOX136'], '137': D['BOX137']}[key]
    info['box'] = set_box(img, lines, bases)
    out = np.clip(img + 0.5, 0, 255).astype(np.uint8)
    edit.save(n, out); print(n, info)
o = [cv2.resize(bt.page(n)[300:1450, 1100:2750], None, fx=0.3, fy=0.3) for n in (122, 123, 136, 137)]
e = [cv2.resize(cv2.imread(f'{S}/hr/pages4k_edit/{n:03d}.png')[300:1450, 1100:2750], None, fx=0.3, fy=0.3) for n in (122, 123, 136, 137)]
cv2.imwrite(f'{S}/txt/l4tpages.png', np.vstack([np.hstack(o), np.hstack(e)]))
