"""محرك رسم الخرائط بأسلوب الدروس المنتجة: قلم يكتب، وفرشاة تلوّن، ثم انتقال.

أُعيد بناؤه من الدروس المنتجة نفسها: اللوح الخلفي واليدان (القلم والفرشاة) مستخرجة من الدرس الثاني.
الاستعمال من بايثون: build_group(...) ثم render(events, t0, t1, out.mp4)
"""
import os, sys, subprocess, cv2, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(HERE)
W, H, FPS = 1920, 1080, 30
PLATE = cv2.imread(f'{S}/l2/plate.png').astype(np.float32)
FONT = '/root/.claude/skills/synced/3677d22d-6e71-479f-845a-4326e7166740_f78b016c-697b-4b0f-bf6a-496e8efb78cc/hdat-identity/assets/fonts/Tajawal-Bold.ttf'
DISK_YEL = np.array([97, 210, 237], np.float32)
DIGIT_BLUE = np.array([123, 75, 7], np.float32)
RING_YEL = np.array([97, 210, 237], np.float32)
AR = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
OFF = np.array([W + 260.0, 620.0])


def load_hand(name):
    z = np.load(f'{S}/l2/{name}.npz')
    return dict(color=z['color'].astype(np.float32), alpha=z['alpha'].astype(np.float32),
                shade=z['shade'].astype(np.float32) if 'shade' in z else None, tip=z['tip'])


HANDS = dict(pen=load_hand('hand_pen'), brush=load_hand('hand_brush'))


# ---------------- عناصر الرسم ----------------
class Stroke:
    """قناع يظهر تدريجياً بترتيب tau (0–1)، مع مسار لرأس الأداة."""

    def __init__(self, alpha, color, tau, path, hand='pen', eps=0.012):
        ys, xs = np.nonzero(alpha > 0.003)
        if len(ys) == 0: self.empty = True; return
        self.empty = False
        self.y0, self.y1, self.x0, self.x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        sl = (slice(self.y0, self.y1), slice(self.x0, self.x1))
        self.a = alpha[sl].astype(np.float32); self.c = color[sl].astype(np.float32); self.tau = tau[sl].astype(np.float32)
        self.path = np.asarray(path, np.float32); self.hand = hand; self.eps = eps

    def paint(self, canvas, p):
        if self.empty or p <= 0: return
        r = np.clip((p - self.tau) / self.eps + 1.0, 0, 1) if p < 1 else 1.0
        a = (self.a * r)[..., None]
        reg = canvas[self.y0:self.y1, self.x0:self.x1]
        reg *= (1 - a); reg += self.c * a

    def tip(self, p):
        n = len(self.path)
        if n == 0: return np.array([W / 2, H / 2], np.float32)
        f = np.clip(p, 0, 1) * (n - 1); i = int(f); j = min(i + 1, n - 1); u = f - i
        return self.path[i] * (1 - u) + self.path[j] * u

    def start(self): return self.tip(0)
    def end(self): return self.tip(1)


def wipe_rtl(alpha, color, hand='pen', wobble=0.0):
    """كتابة من اليمين إلى اليسار: ترتيب الظهور بالموضع الأفقي، ورأس القلم على الحبر عند الحافة."""
    ys, xs = np.nonzero(alpha > 0.05)
    if len(xs) == 0: return None
    x0, x1 = xs.min(), xs.max()
    X = np.arange(alpha.shape[1], dtype=np.float32)
    tau = np.zeros(alpha.shape, np.float32); tau[:] = ((x1 - X) / max(x1 - x0, 1))[None, :]
    # مسار الرأس: لكل عمود متوسط ارتفاع الحبر، مع تنعيم
    cols = np.arange(x1, x0 - 1, -3)
    colw = alpha[:, x0:x1 + 1].sum(0)
    yc = (alpha[:, x0:x1 + 1] * np.arange(alpha.shape[0])[:, None]).sum(0) / np.maximum(colw, 1e-3)
    have = colw > 0.5
    idx = np.arange(len(colw))
    yc = np.interp(idx, idx[have], yc[have])
    yc = cv2.GaussianBlur(yc.reshape(1, -1).astype(np.float32), (0, 0), 6).ravel()
    path = [(c, yc[c - x0] + (wobble * np.sin(c / 9.0))) for c in cols]
    return Stroke(alpha, color, tau, path, hand)


def ordered_contour(filled):
    """حدّ الشكل مرتّباً: يبدأ أعلى اليمين ويتجه يساراً على الحافة العليا."""
    cs, _ = cv2.findContours(filled.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cs, key=len)[:, 0, :].astype(np.float32)
    ymin = c[:, 1].min()
    top = np.nonzero(c[:, 1] <= ymin + 3)[0]
    i0 = top[np.argmax(c[top, 0])]
    c = np.roll(c, -i0, axis=0)
    if len(c) > 10 and c[5, 0] > c[0, 0]: c = np.roll(c[::-1], 1, axis=0)   # الاتجاه يساراً
    return c


def loop(ring_alpha, filled, color, hand='pen'):
    """حلقة (حدّ لافتة أو صندوق أو قرص) تُرسم خطاً واحداً متصلاً."""
    c = ordered_contour(filled)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(c, axis=0), axis=1))]; d /= max(d[-1], 1)
    ys, xs = np.nonzero(ring_alpha > 0.003)
    tau = np.zeros(ring_alpha.shape, np.float32)
    if len(xs):
        from scipy.spatial import cKDTree
        _, k = cKDTree(c).query(np.c_[xs, ys]); tau[ys, xs] = d[k]
    step = max(1, len(c) // 400)
    return Stroke(ring_alpha, color, tau, c[::step], hand, eps=0.004)


def brush_fill(region_alpha, color, zig=7):
    """تلوين بالفرشاة من اليمين إلى اليسار بحركة متعرجة."""
    ys, xs = np.nonzero(region_alpha > 0.05)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    X = np.arange(W, dtype=np.float32); Y = np.arange(H, dtype=np.float32)
    rng = np.random.default_rng(7)
    noise = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 6) * 0.25
    tau = ((x1 - X) / max(x1 - x0, 1))[None, :] + 0 * Y[:, None]
    tau = np.clip(tau + noise * 0.04, 0, 1).astype(np.float32)
    n = 240; p = np.linspace(0, 1, n)
    path = np.c_[x1 - p * (x1 - x0), y0 + (y1 - y0) * (0.5 + 0.42 * np.sin(2 * np.pi * zig * p))]
    return Stroke(region_alpha, color, tau, path, 'brush', eps=0.05)


def spiral_fill(disk, color):
    ys, xs = np.nonzero(disk); cy, cx = ys.mean(), xs.mean(); R = 0.5 * max(np.ptp(ys), np.ptp(xs)) + 1
    Y, X = np.mgrid[:H, :W]
    ang = (np.arctan2(-(Y - cy), X - cx) % (2 * np.pi)) / (2 * np.pi)
    rad = np.hypot(Y - cy, X - cx) / R
    tau = np.clip(1 - rad, 0, 1) * 0.7 + ang * 0.3
    t = np.linspace(0, 1, 120); r = R * (0.85 - 0.75 * t); a = 2 * np.pi * 3 * t + np.pi / 4
    path = np.c_[cx + r * np.cos(a), cy - r * np.sin(a)]
    return Stroke(disk.astype(np.float32), color, tau.astype(np.float32), path, 'brush', eps=0.08)


# ---------------- عناصر الشريحة من صورتها ----------------
def ink(F, bg):
    a = np.clip(np.abs(F.astype(np.float32) - bg).max(2) / 120.0, 0, 1)
    a[F.min(2) > 247] = 0
    return a


def text_ring(soft, width=1.6, ss=4):
    """حدود حروف بيضاء (عنوان اللافتة) بحافة ناعمة."""
    ys, xs = np.nonzero(soft > 0.3)
    y0, y1, x0, x1 = ys.min() - 6, ys.max() + 7, xs.min() - 6, xs.max() + 7
    sub = soft[y0:y1, x0:x1]
    up = cv2.resize(sub, None, fx=ss, fy=ss, interpolation=cv2.INTER_CUBIC) > 0.5
    k = int(round(width * ss)) * 2 + 1
    inner = cv2.erode(up.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))) > 0
    a = cv2.resize((up & ~inner).astype(np.float32), (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    out = np.zeros((H, W), np.float32); out[y0:y1, x0:x1] = np.clip(a * 1.25, 0, 1)
    return out


def split_lines(a):
    """أسطر نص الشرح من فراغات الصفوف."""
    rows = (a > 0.08).sum(1) > 0
    runs, y = [], 0
    while y < H:
        if rows[y]:
            s0 = y
            while y < H and rows[y]: y += 1
            runs.append([s0, y])
        y += 1
    # الحركات المنفصلة فوق السطر أو تحته تُضم إلى أقرب سطر كبير
    big = [r for r in runs if r[1] - r[0] >= 12]
    if not big: return []                     # بلا نص شرح (آثار حواف صغيرة فقط)
    out = []
    for r in big:
        m = np.zeros_like(a); out.append([r[0], r[1], m])
    for r in runs:
        c = (r[0] + r[1]) / 2
        k = int(np.argmin([0 if b[0] <= c <= b[1] else min(abs(c - b[0]), abs(c - b[1])) for b in out]))
        out[k][2][r[0]:r[1]] = a[r[0]:r[1]]
    return [m for _, _, m in out]


class Header:
    def __init__(self, F, bg):
        top = np.zeros((H, W), bool); top[:440] = True
        f = F.astype(int); B, G, R = f[..., 0], f[..., 1], f[..., 2]
        red = (R - G > 60) & (R - B > 60) & top
        hull = cv2.morphologyEx(red.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8)) > 0
        from scipy import ndimage as ndi
        hull = ndi.binary_fill_holes(hull)
        n, lab, st, _ = cv2.connectedComponentsWithStats(hull.astype(np.uint8)); i = 1 + np.argmax(st[1:, 4]); hull = lab == i
        self.hull = hull
        soft = np.clip((F.min(2).astype(np.float32) - 90) / 150, 0, 1) * (cv2.dilate(hull.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
        soft[~hull] = 0
        a = ink(F, bg)
        blue = (B - R > 35) & top & ~(cv2.dilate(hull.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
        n, lab, st, _ = cv2.connectedComponentsWithStats(blue.astype(np.uint8))
        brs = sorted([lab == i for i in range(1, n) if st[i, 4] > 30], key=lambda m: -np.nonzero(m)[1].mean())
        bannerc = np.median(F[red], 0).astype(np.float32)
        er = cv2.erode(hull.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ring = (cv2.dilate(er.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~cv2.erode(er.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        Fc = F.astype(np.float32)
        col = np.zeros((H, W, 3), np.float32) + bannerc
        self.banner_loop = loop(cv2.GaussianBlur(ring.astype(np.float32), (0, 0), 0.6), hull, col)
        self.brackets = [wipe_rtl(np.where(m, a, 0) * 0 + m.astype(np.float32) * np.maximum(a, 0.6), Fc) for m in brs]
        tr = text_ring(soft)
        self.title = wipe_rtl(tr, col)
        # التلوين: اللافتة بلونها النهائي (أحمر وعنوان أبيض)
        self.fill = brush_fill(cv2.GaussianBlur(hull.astype(np.float32), (0, 0), 0.7), Fc)
        self.two_lines = np.ptp(np.nonzero(soft > 0.3)[0]) > 110


class Item:
    def __init__(self, F, bg, idx, disk_r=34):
        f = F.astype(int); B, G, R = f[..., 0], f[..., 1], f[..., 2]
        low = np.zeros((H, W), bool); low[440:] = True
        a = ink(F, bg); Fc = F.astype(np.float32)
        blue = (B - R > 35) & (f.max(2) - f.min(2) > 30) & low
        n, lab, st, _ = cv2.connectedComponentsWithStats(blue.astype(np.uint8))
        outline = np.isin(lab, [i for i in range(1, n) if st[i, 2] > 120])
        ys, xs = np.nonzero(outline); bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
        arrow = blue & ~outline & (np.arange(H)[:, None] > by1 - 25)
        yel = (R > 190) & (G > 160) & (R - B > 70) & low
        from scipy import ndimage as ndi
        hull = ndi.binary_fill_holes(cv2.morphologyEx((outline | yel).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((35, 35), np.uint8)) > 0)
        boxtext = (a > 0.05) & hull & ~outline & ~yel & ~(cv2.dilate(outline.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
        body = (a > 0.02) & low & ~hull & ~blue & ~yel & (np.arange(H)[:, None] > by1)
        # القرص فوق منتصف الحافة العليا
        cx, cy = int(round((bx0 + bx1) / 2)), by0 - int(round(disk_r * 0.63))
        Y, X = np.mgrid[:H, :W]
        dd = np.hypot(Y - cy, X - cx)
        disk = np.clip(disk_r + 0.5 - dd, 0, 1)
        ringa = np.clip(1 - np.abs(dd - (disk_r - 2.5)) / 2.5, 0, 1)
        from PIL import Image, ImageDraw, ImageFont
        im = Image.new('L', (W, H), 0); d = ImageDraw.Draw(im)
        d.text((cx, cy + 3), str(idx).translate(AR), font=ImageFont.truetype(FONT, int(disk_r * 1.3)), fill=255, anchor='mm')
        dig = np.asarray(im).astype(np.float32) / 255 * (disk > 0.5)
        self.disk = disk > 0.5
        col_y = np.zeros((H, W, 3), np.float32) + RING_YEL
        col_d = np.zeros((H, W, 3), np.float32) + DIGIT_BLUE
        self.ring = loop(ringa, disk > 0.5, col_y)
        self.digit = wipe_rtl(dig, col_d)
        fa = np.where(outline, np.maximum(a, 0.85), 0).astype(np.float32)
        self.outline = loop(cv2.GaussianBlur(fa, (0, 0), 0.3), hull, Fc)
        self.boxtext = [wipe_rtl(m, Fc) for m in split_lines(np.where(boxtext, a, 0))]
        self.hl = wipe_rtl(np.where(yel, np.maximum(a, 0.8), 0).astype(np.float32), Fc)
        self.arrow = wipe_rtl(np.where(arrow, np.maximum(a, 0.7), 0).astype(np.float32), Fc) if arrow.any() else None
        self.lines = [wipe_rtl(m, Fc) for m in split_lines(np.where(body, a, 0))]
        # التلوين: القرص أصفر ثم الرقم فوقه
        disk_col = np.zeros((H, W, 3), np.float32) + DISK_YEL
        dd2 = (disk[..., None] * (1 - dig[..., None])) * DISK_YEL + dig[..., None] * DIGIT_BLUE
        self.disk_fill = spiral_fill(self.disk, np.where(dig[..., None] > 0, dd2, disk_col))
        self.lower = cv2.dilate((hull | arrow | body | (disk > 0)).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0


# ---------------- الجدول الزمني ----------------
class Timeline:
    LEAVE, ARRIVE, HOP = 0.45, 0.5, 0.6

    def __init__(self, t):
        self.ev = []; self.t = t; self.hand = None; self.pos = OFF.copy()

    def _off(self): return self.pos[0] >= W

    def leave(self):
        if self.hand is not None and not self._off():
            self.ev.append(('move', self.t, self.t + self.LEAVE, self.hand, self.pos.copy(), OFF.copy())); self.t += self.LEAVE
        self.pos = OFF.copy()

    def draw(self, st, dur, earliest=0.0, gap=0.25):
        if st is None or st.empty: return
        if self.hand is not None and self.hand != st.hand: self.leave()
        start = max(self.t + gap, earliest); wait = start - self.t
        if self._off() or wait > 1.2:
            if not self._off(): self.leave(); start = max(start, self.t + self.ARRIVE)
            self.ev.append(('move', start - self.ARRIVE, start, st.hand, OFF.copy(), st.start()))
        else:
            hop = min(wait, self.HOP)
            if wait > hop: self.ev.append(('hold', self.t, start - hop, self.hand, self.pos.copy()))
            self.ev.append(('move', start - hop, start, st.hand, self.pos.copy(), st.start()))
        self.ev.append(('draw', start, start + dur, st))
        self.t = start + dur; self.hand = st.hand; self.pos = st.end().copy()

    def clear(self, mask, at):
        self.leave(); t0 = max(self.t, at)
        self.ev.append(('clear', t0, t0 + 0.45, mask)); self.t = t0 + 0.45

    def fade(self, at, dur=1.2):
        self.leave(); t0 = max(self.t, at)
        self.ev.append(('fade', t0, t0 + dur)); self.t = t0 + dur


def seq(tl, items, budget, earliest=0.0, minf=0.4, maxf=1.0):
    """items: [(stroke, natural_dur, gap)] تُضغط مددها لتسع الميزانية."""
    items = [x for x in items if x[0] is not None and not x[0].empty]
    if not items: return
    nat = sum(x[1] for x in items); gaps = sum(x[2] for x in items)
    f = float(np.clip((budget - gaps) / nat, minf, maxf)) if budget > 0 else minf
    for i, (st, d, g) in enumerate(items):
        tl.draw(st, d * f, earliest if i == 0 else 0.0, g)


def text_nat(st):
    return max(0.5, (st.x1 - st.x0) / 165.0)


def plan_group(tl, header, items, starts, end, keep=True, next_exists=True, stats=None):
    """مجموعة: لافتة، ثم صناديقها عند أزمنة الكلام، ثم التلوين والثبات والانتقال.
    عند التأخر عن الكلام يُختصر ما ليس نصاً (الإطارات والتلوين والانتقال) ويبقى للشرح أكبر وقت ممكن."""
    a0 = starts[0]
    late = max(0, tl.t - a0)
    hs = [(header.brackets[0] if header.brackets else None, 0.5, 0.2), (header.banner_loop, 2.4, 0.2),
          (header.brackets[1] if len(header.brackets) > 1 else None, 0.4, 0.2),
          (header.title, 4.2 if header.two_lines else 3.0, 0.2)]
    seq(tl, hs, max(2.2, 5.5 - late), earliest=a0 - 0.2, minf=0.3, maxf=0.85)
    for k, (it, a) in enumerate(zip(items, starts)):
        b = starts[k + 1] if k + 1 < len(starts) else end
        last = k + 1 == len(items)
        if k and not keep: tl.clear(items[k - 1].lower, a - 0.5)
        late = max(0, tl.t - a)
        sub = [(it.ring, 0.6, 0.15), (it.digit, 0.3, 0.1), (it.outline, 2.0, 0.2)] + \
              [(s, max(0.8, text_nat(s)), 0.1) for s in it.boxtext if s] + [(it.hl, 0.4, 0.1), (it.arrow, 0.3, 0.1)]
        seq(tl, sub, max(1.6, 3.8 - late), earliest=(a - 0.3), minf=0.35, maxf=0.8)
        reserve = (3.2 if tl.t < b - 8 else 2.0) if last else 0.4
        body = [(s, max(1.8, text_nat(s)), 0.25) for s in it.lines if s]
        nat = sum(x[1] for x in body)
        budget = (b - reserve - tl.t) * 0.95
        seq(tl, body, budget, earliest=tl.t, minf=0.4, maxf=1.0)
        if stats is not None and body:
            gaps = sum(x[2] for x in body)
            stats.append(float(np.clip((budget - gaps) / nat, 0.4, 1.0)) if budget > 0 else 0.4)
    hurry = tl.t > end - 4
    cs = [(header.fill, 2.8, 0.4)] + [(it.disk_fill, 0.6, 0.25) for it in items]
    seq(tl, cs, 1.4 if hurry else 2.6, earliest=tl.t + 0.3, minf=0.25)
    tl.leave()
    if next_exists:
        hold = 0.25 if hurry else 1.0
        tl.fade(max(tl.t + hold, end - 1.0), 0.7 if hurry else 1.2)


# ---------------- الإخراج ----------------
def place_hand(frame, hand, pos):
    hd = HANDS[hand]; ox, oy = hd['tip']
    x0, y0 = int(round(pos[0] - ox)), int(round(pos[1] - oy))
    h, w = hd['alpha'].shape
    fx0, fy0 = max(0, x0), max(0, y0); fx1, fy1 = min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0: return
    sx0, sy0 = fx0 - x0, fy0 - y0
    sl = (slice(fy0, fy1), slice(fx0, fx1)); ss = (slice(sy0, sy0 + fy1 - fy0), slice(sx0, sx0 + fx1 - fx0))
    reg = frame[sl]
    if hd['shade'] is not None: reg *= hd['shade'][ss][..., None]
    a = hd['alpha'][ss][..., None]
    reg *= (1 - a); reg += hd['color'][ss] * a


def ease(u): return 0.5 - 0.5 * np.cos(np.pi * np.clip(u, 0, 1))


def render(events, t_from, t_to, out, base=None, audio=None):
    """يرسم الأحداث بين t_from و t_to؛ base: صورة اللوح عند t_from (ما رُسم قبلها)."""
    ev = sorted(events, key=lambda e: e[1])
    canvas = PLATE.copy() if base is None else base.astype(np.float32).copy()
    done = set()
    # ما انتهى قبل t_from يُرسم مباشرة
    for i, e in enumerate(ev):
        if e[2] <= t_from:
            apply_done(canvas, e); done.add(i)
    args = ['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
    if audio: args += ['-ss', f'{t_from:.3f}', '-t', f'{t_to - t_from:.3f}', '-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k']
    args += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', '-movflags', '+faststart', out]
    enc = subprocess.Popen(args, stdin=subprocess.PIPE)
    n0, n1 = int(round(t_from * FPS)), int(round(t_to * FPS))
    for n in range(n0, n1):
        t = n / FPS
        for i, e in enumerate(ev):
            if i in done or e[2] > t: continue
            apply_done(canvas, e); done.add(i)
        frame = canvas.copy()
        hand = None
        for i, e in enumerate(ev):
            if i in done or e[1] > t: continue
            k = e[0]
            if k == 'draw':
                p = (t - e[1]) / max(e[2] - e[1], 1e-3); e[3].paint(frame, p); hand = (e[3].hand, e[3].tip(p))
            elif k == 'move':
                u = ease((t - e[1]) / max(e[2] - e[1], 1e-3)); hand = (e[3], e[4] * (1 - u) + e[5] * u)
            elif k == 'hold':
                hand = (e[3], e[4])
            elif k == 'clear':
                u = (t - e[1]) / 0.45; m = e[3]
                frame[m] = frame[m] * (1 - u) + PLATE[m] * u
            elif k == 'fade':
                u = (t - e[1]) / max(e[2] - e[1], 1e-3)
                frame[:] = (frame * (1 - u) + PLATE * u) * (1 - 0.075 * np.sin(np.pi * u))
        if hand is not None: place_hand(frame, hand[0], hand[1])
        enc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait()
    return canvas


def apply_done(canvas, e):
    k = e[0]
    if k == 'draw': e[3].paint(canvas, 1.0)
    elif k == 'clear': canvas[e[3]] = PLATE[e[3]]
    elif k == 'fade': canvas[:] = PLATE
