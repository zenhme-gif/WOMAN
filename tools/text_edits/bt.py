"""أدوات تركيب نص الشرح بخط الشرائح الأصلي من قطع الصفحات (4K)."""
import cv2, numpy as np, json, re
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
W = json.load(open(f'{S}/ocr/words_1_143.json'))
strip = lambda s: re.sub('[ً-ْٰ]', '', s)
_pg = {}


def page(n):
    if n not in _pg: _pg[n] = cv2.imread(f'{S}/hr/pages4k/{n:03d}.png')
    return _pg[n]


def alpha(img):
    """حبر الشرح الأسود على خلفية الصفحة الفاتحة."""
    f = img.astype(np.float32); L = f.mean(2)
    return np.clip((228 - L) / (228 - 30), 0, 1)


def find(word, page_n=None):
    out = []
    for n, ws in W.items():
        if page_n and int(n) != page_n: continue
        for k, w in enumerate(ws):
            if strip(word) in strip(w['t']): out.append((int(n), k, w['t'], w['x'], w['y'], w['w'], w['h']))
    return out


def show(n, x0, x1, y0, y1, path, sc=2, step=10):
    a = alpha(page(n)[y0:y1, x0:x1])
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


def baseline(a):
    """صف خط القاعدة: أكثف صف حبراً (وصلات الحروف)."""
    r = (a > 0.5).sum(1); return int(np.argmax(r))


def piece(n, x0, x1, y0, y1, base=None, drop=(), keep=None):
    """قطعة من الصفحة n؛ drop: مستطيلات تُمحى (إحداثيات الصفحة)؛ keep: دالة على مكوّنات تُبقى."""
    a = alpha(page(n)[y0:y1, x0:x1]).copy()
    for (u0, u1, v0, v1) in drop: a[max(0, v0 - y0):max(0, v1 - y0), max(0, u0 - x0):max(0, u1 - x0)] = 0
    b = (base - y0) if base is not None else baseline(a)
    return a, float(b)


def scaled(p, s):
    a, b = p
    if abs(s - 1) < 1e-3: return a, b
    h, w = a.shape
    r = cv2.resize(a, (max(1, round(w * s)), max(1, round(h * s))), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    if s > 1:                                                         # حواف حادة بعد التكبير
        r = np.clip((r - 0.5) * 1.6 + 0.5, 0, 1)
    return np.clip(r, 0, 1).astype(np.float32), b * s


def trim(p):
    a, b = p
    cols = np.nonzero(a.max(0) > 0.12)[0]; rows = np.nonzero(a.max(1) > 0.12)[0]
    return a[rows.min():rows.max() + 1, cols.min():cols.max() + 1], b - rows.min()


def assemble(pieces, gaps):
    """من اليمين إلى اليسار على خط قاعدة واحد؛ gaps[k] بين القطعة k والتي بعدها (سالب = تداخل)."""
    pieces = [trim(p) for p in pieces]
    above = max(b for a, b in pieces); below = max(a.shape[0] - b for a, b in pieces)
    H = int(np.ceil(above + below)) + 4
    total = int(sum(a.shape[1] for a, _ in pieces) + sum(gaps) + 8)
    out = np.zeros((H, total), np.float32)
    x = total - 4.0
    for k, (a, b) in enumerate(pieces):
        w = a.shape[1]; x -= w
        y = int(round(above - b)) + 2; xi = int(round(x))
        reg = out[y:y + a.shape[0], xi:xi + w]
        reg[:] = np.maximum(reg, a[:reg.shape[0], :reg.shape[1]])
        if k < len(gaps): x -= gaps[k]
    cols = np.nonzero(out.max(0) > 0.1)[0]
    return out[:, cols.min():cols.max() + 1], above + 2


def preview(items, path, sc=1.0):
    """items: [(alpha, base)] تُعرض مصفوفة رأسياً على خط قاعدة."""
    ts = []
    for a, b in items:
        im = (255 - np.clip(a, 0, 1) * 255).astype(np.uint8)
        ts.append(cv2.copyMakeBorder(im, max(0, int(round(120 - b))), 0, 10, 10, cv2.BORDER_CONSTANT, value=255))
    H = max(t.shape[0] for t in ts); Wd = max(t.shape[1] for t in ts)
    ts = [cv2.copyMakeBorder(t, 0, H - t.shape[0] + 6, Wd - t.shape[1], 0, cv2.BORDER_CONSTANT, value=255) for t in ts]
    out = np.vstack(ts)
    if sc != 1: out = cv2.resize(out, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, out)


def comps_sel(n, x0, x1, y0, y1, cxa=-1e9, cxb=1e9, extra=None):
    """قطعة بمكوّناتها المتصلة: يُبقى كل مكوّن مركزه الأفقي بين cxa وcxb (إحداثيات الصفحة)."""
    a = alpha(page(n)[y0:y1, x0:x1])
    nl, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.25).astype(np.uint8), 8)
    keep = np.zeros(a.shape, bool)
    for j in range(1, nl):
        cx = cen[j][0] + x0; cy = cen[j][1] + y0
        if cxa <= cx <= cxb and (extra is None or extra(cx, cy, st[j])): keep |= lab == j
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    return np.where(keep, a, 0).astype(np.float32)


def line_base(n, y0, y1, x0=0, x1=3840):
    """خط القاعدة لسطر: أسفل الألفات (مكوّنات طويلة رفيعة)."""
    a = alpha(page(n)[y0:y1, x0:x1])
    nl, lab, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), 8)
    hs = [st[j, 3] for j in range(1, nl)]
    mh = np.percentile(hs, 90) if hs else 0
    bots = [st[j, 1] + st[j, 3] for j in range(1, nl) if st[j, 3] > 3 * st[j, 2] and st[j, 3] > 0.6 * mh]
    return y0 + float(np.median(bots)) if bots else None


def P(n, x0, x1, y0, y1, base, up=1.25, down=0.6, ah=97, **kw):
    """قطعة جاهزة: (ألفا، خط القاعدة داخلها). تُبقى مكوّنات السطر وحده: مركزها بين base−up·ah وbase+down·ah."""
    lo, hi = base - up * ah, base + down * ah
    kw.setdefault('extra', lambda cx, cy, st: lo <= cy <= hi)
    return comps_sel(n, x0, x1, y0, y1, **kw), float(base - y0)


def spans(n, y0, y1, x0, x1, gap=14):
    cols = (alpha(page(n)[y0:y1, x0:x1]) > 0.3).sum(0) > 0
    xs = np.nonzero(cols)[0]; out = []; s = xs[0]; p = xs[0]
    for x in xs[1:]:
        if x - p > gap: out.append((int(s + x0), int(p + x0))); s = x
        p = x
    out.append((int(s + x0), int(p + x0)))
    return out[::-1]
