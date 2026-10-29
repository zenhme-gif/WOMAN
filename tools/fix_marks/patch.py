"""تصحيح نص الشرح في مقاطع من الدرس الأول دون إعادة رسمه.

لكل كتلة نص: تُبنى الكلمات الصحيحة من صفحة الشريحة الأصلية، وتوضع كل كلمة فوق موضعها في الفيديو
(مطابقة القالب)، ثم يُصحَّح كل إطار:
- حبر زائد في النسخة القديمة (حركة متسربة أو طرف سهم): يُمحى بقدر ظهوره في الإطار.
- حبر ناقص (حركة مقطوعة): يظهر بقدر اكتمال كتابة كلمته، ويخفت مع انتقال الشريحة.
- ما تغطيه اليد لا يُمسّ.
الاستعمال: python3 patch.py preview | python3 patch.py run in.mp4 t0 t1 out_frames_pipe
"""
import sys, subprocess, json, cv2, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__file__))
import words as WD

S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
VID = f'{S}/work/lesson1_cur.mp4'
W, H = 1920, 1080
# الصفحة، معامل التصغير، المنطقة في الفيديو (x0, y0, x1, y1)، إطار الثبات (مكتمل بلا يد)، نافذة التصحيح
BLOCKS = [
    dict(name='k18', page=18, s=0.60, box=(120, 611, 935, 735), hold=692.5, win=(683.0, 712.5)),
    dict(name='k16', page=16, s=0.60, box=(1090, 946, 1705, 1018), hold=707.0, win=(696.0, 712.5)),
    dict(name='k19', page=19, s=0.60, box=(130, 946, 925, 1022), hold=707.0, win=(703.0, 712.5)),
    dict(name='t22', page=22, s=0.68, box=(985, 875, 1795, 1000), hold=830.0, win=(751.0, 841.5)),
    dict(name='t23', page=23, s=0.68, box=(105, 875, 955, 1022), hold=830.0, win=(779.0, 841.5)),
]


def frame_at(t):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', VID, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                       capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(H, W, 3).copy()


def lum(x):
    return x[..., 0] * 0.114 + x[..., 1] * 0.587 + x[..., 2] * 0.299


def prepare(b):
    x0, y0, x1, y1 = b['box']
    old = frame_at(b['hold'])[y0:y1, x0:x1].astype(np.float32)
    ink = (lum(old) < 200).astype(np.uint8)
    bg = cv2.inpaint(old.astype(np.uint8), cv2.dilate(ink, np.ones((7, 7), np.uint8)), 9, cv2.INPAINT_TELEA).astype(np.float32)
    bg = cv2.GaussianBlur(bg, (0, 0), 6)
    old_a = np.clip((lum(bg) - lum(old)) / 160.0, 0, 1)
    F = cv2.imread(f"{S}/pages/{b['page']:03d}.png")
    wl, _ = WD.words(F, 712, 1075)
    s = b['s']
    new_a = np.zeros_like(old_a); ink_new = np.zeros_like(old); wid = np.full(old_a.shape, -1, np.int32)
    search = old_a.copy()
    placed = []; line_cy = 0
    for k, (im, a, _) in enumerate(wl):
        ta = cv2.resize(a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        ti = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA).astype(np.float32)
        r = cv2.matchTemplate(search, ta, cv2.TM_CCORR_NORMED)
        h, w = ta.shape
        # ترتيب القراءة: الكلمة التالية يسار السابقة في السطر نفسه، أو أول السطر الذي يليه
        if placed:
            _, px, py, pw, ph, _ = placed[-1]
            yy, xx = np.mgrid[:r.shape[0], :r.shape[1]]
            ov = np.minimum(yy + h, py + ph) - np.maximum(yy, py)          # تداخل رأسي مع الكلمة السابقة
            same = (ov >= 0.5 * min(h, ph)) & (xx + w <= px + 10)
            nxt = (yy > py + 0.5 * ph) & (yy < py + ph + 120)
            ra = np.where(same, r, -1); rb = np.where(nxt, r, -1)
            def nearest(rr, best_right):
                """أفضل تطابق، ومع تكرار الكلمة يُختار الأقرب إلى الكلمة السابقة."""
                top = rr.max()
                ys_, xs_ = np.nonzero(rr >= top - 0.03)
                j = np.argmax(xs_) if best_right else np.argmax(xs_)
                return (ys_[j], xs_[j]), top
            ia, sa = nearest(ra, True); ib, sb = nearest(rb, True)
            (my, mx), sc = (ia, sa) if sa >= sb - 0.02 else (ib, sb)
        else:
            xx = np.arange(r.shape[1])[None, :]
            ra = np.where(xx > r.shape[1] * 0.45, r, -1)       # أول كلمة في يمين الكتلة
            my, mx = np.unravel_index(np.argmax(ra), r.shape); sc = ra[my, mx]
        if not placed or abs(my + h / 2 - line_cy) > 26: line_cy = my + h / 2       # سطر جديد
        placed.append((k, mx, my, w, h, round(float(sc), 3)))
        reg = (slice(my, my + h), slice(mx, mx + w))
        # لون الحبر من الصفحة: يُعاد حسابه فوق خلفية الفيديو
        dark = np.median(ti[ta > 0.9], 0) if (ta > 0.9).any() else np.array([40, 40, 40], np.float32)
        na = np.maximum(new_a[reg], ta); new_a[reg] = na
        ink_new[reg] = np.where(ta[..., None] > 0, dark, ink_new[reg])
        wid[reg] = np.where(ta > 0.05, k, wid[reg])
        search[reg] = np.where(ta > 0.05, 0, search[reg])        # لا تُطابق كلمتان الموضع نفسه
    new = bg * (1 - new_a[..., None]) + ink_new * new_a[..., None]
    # منطقة كل كلمة (لحساب نسبة اكتمال كتابتها)
    near = cv2.dilate((wid + 1).astype(np.float32), np.ones((9, 9), np.uint8)).astype(np.int32) - 1
    # الفرق المعتبر: حركة أو أثر يبعد أكثر من نقطتين عن حبر النسخة الأخرى (لا فروق حواف الحروف)
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    near_new = cv2.dilate((new_a > 0.06).astype(np.uint8), k5) > 0
    near_old = cv2.dilate((old_a > 0.12).astype(np.uint8), k5) > 0

    def blobs(m, min_px=6):
        """كتل الحبر التي لا تقل عن min_px نقطة (لا شظايا الحواف)."""
        n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), 8)
        keep = np.zeros(n, bool); keep[1:] = st[1:, 4] >= min_px
        return keep[lab]
    k3 = np.ones((3, 3), np.uint8)
    # زائد: حبر قديم يبعد أكثر من نقطتين عن الجديد؛ ناقص: حبر جديد يبعد أكثر من نقطتين عن القديم
    near_new1 = cv2.dilate((new_a > 0.06).astype(np.uint8), k3) > 0
    near_old1 = cv2.dilate((old_a > 0.12).astype(np.uint8), k3) > 0
    core_s = blobs((old_a > 0.12) & ~near_new1, 2)
    stray_m = (cv2.dilate(core_s.astype(np.uint8), k3) > 0) & (old_a > 0.04) & ~(new_a > 0.3)
    core_m = blobs((new_a > 0.06) & ~near_old1, 4)
    miss_m = (cv2.dilate(core_m.astype(np.uint8), k5) > 0) & (new_a > 0.06) & ~(old_a > 0.3)
    near_new = ~stray_m          # تُستعمل في التصحيح: الزائد = مكوّنات الزائد فقط
    near_old = ~miss_m
    return dict(old=old, bg=bg, new=new, old_a=old_a, new_a=new_a, wid=near, n=len(wl), placed=placed,
                near_new=near_new, near_old=near_old)


REF = np.array([228, 236, 240], np.float32)       # لون زاوية الإطار العليا اليسرى في الحالة العادية


def global_delta(frame):
    """الانتقال يخفت الإطار كله؛ تُقاس إزاحته من زاويتين لا تبلغهما اليد."""
    a = frame[20:60, 20:60].reshape(-1, 3).astype(np.float32)
    b = frame[600:640, 5:25].reshape(-1, 3).astype(np.float32)
    return np.median(np.vstack([a, b]), 0) - REF


def fade_state(f, P, delta):
    """تباين حبر الكتلة c (1 بلا انتقال، 0 عند اختفائها) بعد طرح إزاحة الانتقال."""
    old, bg, oa, na = P['old'], P['bg'], P['old_a'], P['new_a']
    both = (oa > 0.4) & (na > 0.4)
    den = lum(bg - old)[both]
    num = lum(bg + delta - f)[both]
    c = float(np.clip(np.median(num / np.maximum(den, 1e-3)), 0, 1)) if both.sum() > 20 else 0.0
    return delta.astype(np.float32), c


def patch_region(f0, P, delta=None):
    """يصحّح منطقة إطار واحد (float32) ويعيدها: يُزال أثر الانتقال، ثم يُصحَّح، ثم يُعاد الانتقال."""
    if delta is None: delta = np.zeros(3, np.float32)
    delta, c = fade_state(f0, P, delta)
    if c < 0.05 and np.abs(delta).max() > 6:      # المشهد اختفى في الانتقال: لا شيء يُصحَّح
        return f0
    fade = np.abs(delta).max() > 6 and c < 0.97
    cc = max(c, 0.05) if fade else 1.0
    f = P['bg'] + (f0 - P['bg'] - delta) / cc if fade else f0
    out = _patch(f, P)
    return P['bg'] + delta + (out - P['bg']) * cc if fade else out


def _patch(f, P):
    old, bg, new, oa, na, wid = P['old'], P['bg'], P['new'], P['old_a'], P['new_a'], P['wid']
    # اليد: لون لا يفسّره خلطٌ بين الخلفية والحبر القديم (يصح أثناء الكتابة والانتقال)، مع هامش حولها
    v = old - bg; vv = (v * v).sum(2) + 1e-3
    lam = np.clip(((f - bg) * v).sum(2) / vv, 0, 1)
    res = np.abs(f - (bg + v * lam[..., None])).max(2)
    hand = (res > 24).astype(np.uint8)
    occl = cv2.dilate(hand, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))) > 0       # هامش واسع للإضافة
    occl_s = cv2.dilate(hand, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))) > 0        # هامش ضيق للمحو
    den = np.maximum(lum(bg) - lum(old), 1e-3)
    ap = np.clip((lum(bg) - lum(f)) / den, 0, 1)                 # ظهور الحبر القديم في كل نقطة
    out = f.copy()
    stray = (oa > 0.04) & ~P['near_new'] & (res <= 18)     # النقطة تُفسَّر حبراً قديماً على اللوح (لا يداً ولا قلماً)
    out[stray] = (f + (bg - old) * ap[..., None])[stray]          # يُمحى الزائد بقدر ظهوره
    both = (oa > 0.25) & (na > 0.25) & ~occl
    miss = (na > 0.06) & ~P['near_old'] & ~occl
    for k in range(P['n']):
        m = both & (wid == k)
        if m.sum() < 12: continue
        aw = float(np.clip(np.median(ap[m]), 0, 1))               # اكتمال كتابة الكلمة (وخفوتها عند الانتقال)
        mm = miss & (wid == k)
        out[mm] = (f + (new - bg) * aw)[mm]
    return np.clip(out, 0, 255)


if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        tiles = []
        for b in BLOCKS:
            P = prepare(b)
            print(b['name'], 'words', P['n'], 'scores', [p[5] for p in P['placed']])
            x0, y0, x1, y1 = b['box']
            fixed = patch_region(P['old'], P)
            tiles.append(np.vstack([P['old'], fixed]).astype(np.uint8))
        w = max(t.shape[1] for t in tiles)
        cv2.imwrite(f'{S}/fix1/preview.png', np.vstack([np.pad(t, ((0, 6), (0, w - t.shape[1]), (0, 0)), constant_values=255) for t in tiles]))
