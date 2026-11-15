"""الدرس الثاني: تطبيق نصوص ورقة التعديل على صفحات المصدر (4K، ومنها 1080): اللافتة والمربع والشرح والسهم."""
import sys, pickle, os, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt, edit
import tf
S = bt.S
B = pickle.load(open(f'{S}/txt/l2body.pkl', 'rb'))
Tt = pickle.load(open(f'{S}/txt/l2title.pkl', 'rb'))
AH = 97


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




def body(img, n, kill_bases, lines):
    for b in kill_bases:
        tmp_src = img
        a = bt.alpha(np.clip(img + 0.5, 0, 255).astype(np.uint8))
        y0, y1 = int(b - 1.8 * AH), int(b + 1.0 * AH)
        sub = a[y0:y1, 300:3540]
        nl, lab, st, cen = cv2.connectedComponentsWithStats((sub > 0.2).astype(np.uint8), 8)
        kill = np.zeros(sub.shape, bool)
        for j in range(1, nl):
            if b - 1.25 * AH <= cen[j][1] + y0 <= b + 0.6 * AH: kill |= lab == j
        kill = cv2.dilate(kill.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        reg = img[y0:y1, 300:3540]; reg[kill] = edit.BGP
    col = edit.ink_color(bt.page({59: 58, 77: 78}.get(n, n)))
    for piece, b in lines:
        paste(img, piece, 1920.0, b, col)


def arrow_from(img, src):
    s = bt.page(src)[1344:1428, 1870:1970].astype(np.float32)
    d = np.abs(s - edit.BGP).max(2) > 6
    reg = img[1344:1428, 1870:1970]; reg[d] = s[d]


JOBS = {
    58: dict(kill=[1547], lines=[(B['G9a'], 1547)]),
    59: dict(kill=[], lines=[(B['G9b1'], 1547), (B['G9b2'], 1715)], arrow=58),
    77: dict(kill=[], lines=[(B['N1a'], 1547), (B['N1b'], 1715)], arrow=78, title=True, box=(Tt['BOX_N1'], [1094, 1270])),
    78: dict(kill=[1547, 1715, 1888], lines=[(B['N2a'], 1547), (B['N2b'], 1715), (B['N2c'], 1884)], title=True, box=(Tt['BOX_N2'], [1094, 1270])),
    80: dict(kill=[1547, 1715], lines=[(B['N3a'], 1547), (B['N3b'], 1715)], title=True, box=(Tt['BOX_N3'], [1094, 1270])),
}
if __name__ == '__main__':
    for n, j in JOBS.items():
        for p in (f'{S}/hr/pages4k_edit/{n:03d}.png', f'{S}/pages_edit/{n:03d}.png'):
            if os.path.exists(p): os.remove(p)
        img = bt.page(n).astype(np.float32).copy()
        info = {}
        if j.get('title'):
            info['title'] = set_title(img, Tt['BANNER'])
            # بقايا بيضاء من العنوان القديم على حافة اللافتة (خارج داخلها المقلّص): تُرمَّم مما حولها
            w, h0 = Tt['BANNER'][0].shape[1], Tt['BANNER'][0].shape[0]
            cx = info['title']['cx']; x0, x1 = int(cx - w / 2) - 8, int(cx + w / 2) + 8
            reg = np.clip(img[360:760, 1300:2600] + 0.5, 0, 255).astype(np.uint8)
            wm = reg.min(2) > 200
            n_, lab, st, _ = cv2.connectedComponentsWithStats(wm.astype(np.uint8))
            m = np.zeros(wm.shape, np.uint8)
            for k in range(1, n_):
                X, Y, Wd, Hd, A = st[k]
                if A < 3000 and not (x0 <= X + 1300 and X + Wd + 1300 <= x1 and Y + 360 >= 480): m[lab == k] = 1
            if m.any():
                m = cv2.dilate(m, np.ones((5, 5), np.uint8))
                img[360:760, 1300:2600] = cv2.inpaint(reg, m, 4, cv2.INPAINT_TELEA).astype(np.float32)
                info['leftover_px'] = int(m.sum())
        if j.get('box'): info['box'] = set_box(img, *j['box'])
        body(img, n, j['kill'], j['lines'])
        if j.get('arrow'): arrow_from(img, j['arrow'])
        edit.save(n, np.clip(img + 0.5, 0, 255).astype(np.uint8)); print(n, info)
    o = [cv2.resize(bt.page(n), None, fx=0.25, fy=0.25) for n in JOBS]
    e = [cv2.resize(cv2.imread(f'{S}/hr/pages4k_edit/{n:03d}.png'), None, fx=0.25, fy=0.25) for n in JOBS]
    cv2.imwrite(f'{S}/txt/l2pages.jpg', np.vstack([np.hstack(o[:3]), np.hstack(e[:3])]))
    cv2.imwrite(f'{S}/txt/l2pages2.jpg', np.vstack([np.hstack(o[3:]), np.hstack(e[3:])]))
