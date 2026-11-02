"""الشرائح المركّبة (المدمجة والمعدّلة) بدقة 4K: كل كتلة ثم كل كلمة ثم كل حرف في الشريحة يُبحث عن موضعه
ومقاسه في الصفحات الأصلية ويُنسخ من نسختها العالية الدقة؛ وما لا يُعثر عليه يُكبَّر من الشريحة نفسها بحواف حادة."""
import cv2, numpy as np, json, sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/hr')
import build_std as B
from sharpup import sharp_up
S = B.S
PL1 = cv2.imread(f'{S}/l2/plate.png')
gray = lambda x: cv2.cvtColor(np.clip(x, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)
_P1, _P4, _G = {}, {}, {}


def page1(n):
    if n not in _P1:
        F = cv2.imread(f'{S}/pages/{n:03d}.png'); F = np.vstack([F, F[-1:]])[:1080]
        # نفس تحويل الخلفية المطبَّق على 4K (الأبيض الواسع ولون الصفحة ← اللوح) حتى تتطابق الرسوم
        up = cv2.resize(F, (3840, 2160), interpolation=cv2.INTER_NEAREST).astype(np.float32)
        _P1[n] = F
    return _P1[n]


def page4(n):
    if n not in _P4: _P4[n] = B.compose_page(n, 0, 0)
    return _P4[n]


def page1c(n):
    """الصفحة بدقة 1080 بعد تحويل خلفيتها إلى اللوح (من نسخة 4K المركّبة) — هي ما يطابق الشريحة."""
    if n not in _G: _G[n] = cv2.resize(np.clip(page4(n), 0, 255).astype(np.uint8), (1920, 1080), interpolation=cv2.INTER_AREA)
    return _G[n]


def hl_mask(img, loose=False):
    """خط التظليل الأصفر تحت الصناديق: أصفر ممدود (لا الأقراص)."""
    f = img.astype(np.int16); B_, G_, R_ = f[..., 0], f[..., 1], f[..., 2]
    y = (R_ > 180) & (G_ > 150) & (R_ - B_ > (40 if loose else 70))
    n, lab, st, _ = cv2.connectedComponentsWithStats(y.astype(np.uint8))
    keep = [j for j in range(1, n) if st[j, 2] > 2.5 * st[j, 3] and st[j, 4] > (60 if loose else 200)]
    return np.isin(lab, keep)


_scaled = {}
def scaled1(n, s):
    """الصفحة مصغّرة بالمقياس s بأطوار البكسل الممكنة: الكلمة المصغّرة وحدها تبدأ من موضع صحيح في الصفحة،
    فيختلف طور شبكة التصغير؛ تُحضَّر الأطوار (إزاحة 0–3 بكسل قبل التصغير) لتتطابق تماماً."""
    k = (n, round(s, 3))
    if k not in _scaled:
        im = page1c(n).copy(); im[cv2.dilate(hl_mask(im).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0] = PL1[0, 0]
        if s == 1: _scaled[k] = [(0, 0, gray(im))]
        else: _scaled[k] = [(ox, oy, gray(cv2.resize(im[oy:, ox:], None, fx=s, fy=s, interpolation=cv2.INTER_AREA))) for oy in range(4) for ox in range(4)]
    return _scaled[k]


def match(crop_g, n, s, window=None):
    best = (-1, None)
    if crop_g.std() < 1: return best
    for ox, oy, P in scaled1(n, s):
        if window is not None:
            x0, y0, x1, y1 = window
            x0 = int(max(0, x0 - s * ox)); y0 = int(max(0, y0 - s * oy)); x1, y1 = min(P.shape[1], int(x1)), min(P.shape[0], int(y1))
            Q = P[y0:y1, x0:x1]
        else: x0 = y0 = 0; Q = P
        if Q.shape[0] < crop_g.shape[0] or Q.shape[1] < crop_g.shape[1]: continue
        m = cv2.matchTemplate(Q, crop_g, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(m)
        if mx > best[0]: best = (mx, (loc[0] + x0 + s * ox, loc[1] + y0 + s * oy))   # موضعه في الصفحة المصغّرة كاملةً
    return best


def build(s1, cands, scales, log, hl=True):
    H, W = 1080, 1920
    out = B.PLATE4.copy()
    ink = np.abs(s1.astype(np.int16) - PL1.astype(np.int16)).max(2) > 22
    ink[:150] = False; ink[1015:] = False; ink[:, :40] = False; ink[:, 1880:] = False
    disks = B.find_disks(s1)
    hl1 = cv2.dilate(hl_mask(s1, loose=True).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    if not hl: hl1[:] = False
    s1_orig = s1; s1 = s1.copy(); s1[hl1] = PL1[hl1]; ink &= ~hl1
    for cx, cy, r in disks:
        cv2.circle(ink.view(np.uint8), (int(cx), int(cy)), int(r + 3), 0, -1)
    todo = ink.copy(); done = np.zeros_like(ink)

    def paste(x, y, w, h, n, s, u, v, mask):
        P4 = page4(n) if s == 1 else cv2.resize(page4(n), None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        U, V = int(round(2 * u)), int(round(2 * v))
        src = P4[V:V + 2 * h, U:U + 2 * w]
        if src.shape[0] != 2 * h or src.shape[1] != 2 * w: return False
        m = cv2.resize(mask.astype(np.float32), (2 * w, 2 * h), interpolation=cv2.INTER_LINEAR)[..., None]
        reg = out[2 * y:2 * y + 2 * h, 2 * x:2 * x + 2 * w]
        reg[:] = src * m + reg * (1 - m)
        return True

    def try_comp(mask_full, thr, local=None, scales_=None):
        ys, xs = np.nonzero(mask_full)
        x, y = max(0, xs.min() - 4), max(0, ys.min() - 4); x1, y1 = min(W, xs.max() + 5), min(H, ys.max() + 5)
        w, h = x1 - x, y1 - y
        crop = gray(s1[y:y1, x:x1])
        best = (-1, None)
        for n in cands:
            for s in (scales_ or scales):
                win = None
                if local is not None:
                    ox, oy = local[n, s] if (n, s) in local else (None, None)
                    if ox is None: continue
                    win = (x + ox - 40, y + oy - 40, x1 + ox + 40, y1 + oy + 40)
                sc, loc = match(crop, n, s, win)
                if sc > best[0]: best = (sc, (n, s, loc))
        if best[0] >= thr:
            n, s, (u, v) = best[1]
            fb = s1[mask_full].astype(np.int16)
            near_hl = hl and w > 60 and hl1[max(0, y - 14):y1 + 14, max(0, x - 14):x1 + 14].any()   # ما يجاور التظليل يؤخذ معه تظليله كما في الصفحة
            if near_hl:
                P = 14; x_, y_ = max(0, x - P), max(0, y - P); x1_, y1_ = min(W, x1 + P), min(H, y1 + P)
                mk = np.zeros((y1_ - y_, x1_ - x_), np.uint8)
                mk[y - y_:y1 - y_, x - x_:x1 - x_] = mask_full[y:y1, x:x1]
                mk = cv2.dilate(mk, np.ones((5, 5), np.uint8)) | (cv2.dilate(hl1[y_:y1_, x_:x1_].astype(np.uint8), np.ones((9, 9), np.uint8)))
                ps = page1c(n) if s == 1 else cv2.resize(page1c(n), None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
                U0, V0 = int(round(u - (x - x_))), int(round(v - (y - y_)))
                phl = hl_mask(ps[max(0, V0):V0 + mk.shape[0], max(0, U0):U0 + mk.shape[1]])
                if phl.shape == mk.shape: mk |= cv2.dilate(phl.astype(np.uint8), np.ones((7, 7), np.uint8))
                msk = cv2.GaussianBlur(mk.astype(np.float32), (0, 0), 1.0)
                if paste(x_, y_, x1_ - x_, y1_ - y_, n, s, u - (x - x_), v - (y - y_), msk): return best[0], (n, s, u - x, v - y)
                return best[0], None
            msk = cv2.dilate(mask_full[y:y1, x:x1].astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
            msk = cv2.GaussianBlur(msk, (0, 0), 1.0)
            if paste(x, y, w, h, n, s, u, v, msk): return best[0], (n, s, u - x, v - y)
        return best[0], None

    offsets = {}
    stats = {'block': 0, 'word': 0, 'glyph': 0, 'fallback': 0, 'banner': None}
    # 0) اللافتة الحمراء: من الصفحة ذات اللافتة نفسها، ونصها يُعاد كلمةً كلمة إن اختلف
    from scipy import ndimage as ndi
    f = s1.astype(np.int16); Bc, Gc, Rc = f[..., 0], f[..., 1], f[..., 2]
    red = (Rc > 150) & (Rc - Bc > 60) & (Rc - Gc > 50); red[:150] = False; red[450:] = False
    nr, lr, sr, _ = cv2.connectedComponentsWithStats(red.astype(np.uint8))
    if nr > 1:
        j = 1 + int(np.argmax(sr[1:, 4])); bmask = ndi.binary_fill_holes(lr == j)
        ys, xs = np.nonzero(bmask); bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        sc, res = try_comp(bmask & ink | (bmask & ~ink), 0.985)
        if res:
            todo &= ~cv2.dilate(bmask.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool); stats['banner'] = ('whole', round(sc, 3), res)
        else:
            best = None
            for n in cands:
                g = page1c(n).astype(np.int16); pr = (g[..., 2] > 150) & (g[..., 2] - g[..., 0] > 60) & (g[..., 2] - g[..., 1] > 50)
                pf = ndi.binary_fill_holes(pr); pf[450:] = False
                iou = (pf & bmask).sum() / max(1, (pf | bmask).sum())
                if best is None or iou > best[0]: best = (iou, n)
            n = best[1]; P4 = page4(n)
            g4 = P4.astype(np.int16); pr4 = (g4[..., 2] > 150) & (g4[..., 2] - g4[..., 0] > 60) & (g4[..., 2] - g4[..., 1] > 50); pr4[900:] = False
            nn, ll, ss, _ = cv2.connectedComponentsWithStats(pr4.astype(np.uint8)); jj = 1 + int(np.argmax(ss[1:, 4]))
            pf4 = ndi.binary_fill_holes(ll == jj)
            redc = np.median(P4[ll == jj].reshape(-1, 3), 0)
            inner = cv2.erode(pf4.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
            ban = P4.copy(); ban[inner & (np.abs(P4 - redc).max(2) > 6)] = redc     # محو نص اللافتة وحوافه
            m4 = cv2.GaussianBlur(cv2.dilate(pf4.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32), (0, 0), 1.5)[..., None]
            out[:] = ban * m4 + out * (1 - m4)
            txt = bmask & ~cv2.dilate(red.astype(np.uint8) & bmask.astype(np.uint8), np.ones((1, 1), np.uint8)).astype(bool) & ink
            txt = bmask & (f.min(2) > 150)                                        # النص الأبيض داخل اللافتة
            todo &= ~((cv2.dilate(bmask.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0) & ~txt)
            todo |= txt
            stats['banner'] = ('rebuilt', round(float(best[0]), 3), n)
    # 1) الكتل
    nb, lb, sb, _ = cv2.connectedComponentsWithStats(cv2.dilate(todo.astype(np.uint8), np.ones((25, 25), np.uint8)))
    for b in range(1, nb):
        bm = (lb == b) & todo
        if bm.sum() < 30: continue
        sc, res = try_comp(bm, 0.985)
        if res:
            todo &= ~bm; stats['block'] += 1; offsets.setdefault((res[0], res[1]), []).append(res[2:])
            log.append(('block', b, round(sc, 3), res)); continue
        # 2) الكلمات داخل الكتلة
        nw, lw, sw, _ = cv2.connectedComponentsWithStats(cv2.dilate(bm.astype(np.uint8), np.ones((5, 5), np.uint8)))
        for wi in range(1, nw):
            wm = (lw == wi) & bm
            if wm.sum() < 8: continue
            sc, res = try_comp(wm, 0.95)
            if res:
                todo &= ~wm; stats['word'] += 1; offsets.setdefault((res[0], res[1]), []).append(res[2:])
                log.append(('word', b, wi, round(sc, 3), res))
    # 3) الحروف المتبقية: بحث قريب من إزاحة جاراتها
    local = {k: tuple(np.median(np.array(v), 0).astype(int)) for k, v in offsets.items()}
    ng, lg, sg, _ = cv2.connectedComponentsWithStats(todo.astype(np.uint8))
    for gi in range(1, ng):
        gm = lg == gi
        if gm.sum() < 3: todo &= ~gm; continue
        sc, res = try_comp(gm, 0.9, local=local)
        if res: todo &= ~gm; stats['glyph'] += 1; log.append(('glyph', gi, round(sc, 3), res))
    # 4) ما بقي: تكبير من الشريحة نفسها (دون بقايا خط التظليل القديم، فقد أُخذ تظليل الصفحة)
    if hl: todo &= ~(cv2.dilate(hl1.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0)
    if todo.any():
        up = sharp_up(s1).astype(np.float32)
        m = cv2.dilate(todo.astype(np.uint8), np.ones((5, 5), np.uint8))
        stats['fallback'] = int(todo.sum())
        m4 = cv2.GaussianBlur(cv2.resize(m.astype(np.float32), (3840, 2160), interpolation=cv2.INTER_LINEAR), (0, 0), 1.0)[..., None]
        out = up * m4 + out * (1 - m4)
    for cx, cy, r in disks:
        d, _ = B.digit_of(s1, cx, cy, r); B.draw_disk(out, cx, cy, r, d)
    return out, stats, todo


if __name__ == '__main__':
    key = sys.argv[1]; cands = [int(x) for x in sys.argv[2].split(',')]
    scales = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [1.0]
    k, i = key.split('/')
    s1 = cv2.imread(f'{S}/slides/out/درس{k}/{i}.png')
    log = []
    img, stats, todo = build(s1, cands, scales, log)
    mean, bad = B.verify(img, s1)
    os.makedirs(f'{S}/hr/out/درس{k}', exist_ok=True)
    cv2.imwrite(f'{S}/hr/out/درس{k}/{i}.png', np.clip(img + 0.5, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 6])
    cv2.imwrite(f'{S}/hr/todo_{k}_{i}.png', (todo * 255).astype(np.uint8))
    print(key, stats, 'verify mean %.2f bad %d' % (mean, bad))
    for l in log[:200]: print('  ', l)
