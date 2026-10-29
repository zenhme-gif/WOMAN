"""كلمات نص الشرح من صفحة الشريحة الأصلية مع كل حركاتها.

كل مكوّن متصل (حرف أو حركة) يُنسب إلى سطره بالقرب الرأسي، ثم إلى كلمته بموضعه الأفقي؛
فلا تنقطع حركة عند حدّ السطر ولا تتسرب حركة سطر إلى غيره. الأزرق (رأس السهم) مستبعد.
"""
import cv2, numpy as np

BG_PAGE = None


def text_alpha(F):
    """شدة الحبر (0–1) من البعد عن لون الخلفية، دون الأزرق."""
    f = F.astype(np.float32)
    bg = np.median(F[:40, :40].reshape(-1, 3), 0).astype(np.float32)
    a = np.clip(np.abs(f - bg).max(2) / 120.0, 0, 1)
    B, G, R = f[..., 0], f[..., 1], f[..., 2]
    blue = (B - R > 35) & (a > 0.05)
    blue = cv2.dilate(blue.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    a[blue] = 0
    return a, bg


def words(F, y0, y1, gap=14):
    """كلمات المنطقة y0:y1 بترتيب القراءة: [(صورة الحبر BGR, شدة الحبر, (x, y) أعلى يسارها)]."""
    a, bg = text_alpha(F)
    a[:y0] = 0; a[y1:] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.08).astype(np.uint8), 8)
    comps = [i for i in range(1, n) if st[i, 4] >= 3]
    hmax = max(st[i, 3] for i in comps)
    big = [i for i in comps if st[i, 3] > 0.45 * hmax or st[i, 4] >= 400]   # جسم حرف؛ وما دونه حركة أو نقطة
    # الأسطر: المكوّنات الكبيرة المتداخلة رأسياً
    lines = []
    for i in sorted(big, key=lambda i: st[i, 1] + st[i, 3] / 2):
        t, b = st[i, 1], st[i, 1] + st[i, 3]
        for L in lines:
            if min(b, L['b']) - max(t, L['t']) > 0.5 * min(b - t, L['b'] - L['t']):
                L['m'].append(i); L['t'] = min(L['t'], t); L['b'] = max(L['b'], b); break
        else:
            lines.append(dict(t=t, b=b, m=[i]))
    lines.sort(key=lambda L: L['t'])
    owner = {}                                   # كل حركة أو نقطة تتبع أقرب حبر حرف إليها فعلاً (لا أقرب مستطيل)
    pix = {j: np.column_stack(np.nonzero(lab[st[j, 1]:st[j, 1] + st[j, 3], st[j, 0]:st[j, 0] + st[j, 2]] == j)) + [st[j, 1], st[j, 0]] for j in big}
    for i in comps:
        if i in big: owner[i] = i; continue
        q = np.column_stack(np.nonzero(lab[st[i, 1]:st[i, 1] + st[i, 3], st[i, 0]:st[i, 0] + st[i, 2]] == i)) + [st[i, 1], st[i, 0]]
        cy, cx = q.mean(0)
        best, bd = None, 1e9
        for j in big:
            if abs(st[j, 0] + st[j, 2] / 2 - cx) > st[j, 2] / 2 + 60 or abs(st[j, 1] + st[j, 3] / 2 - cy) > st[j, 3] / 2 + 60: continue
            pj = pix[j]
            d = np.sqrt(((pj[None, :, :] - q[::max(1, len(q) // 40), None, :]) ** 2).sum(2)).min()
            if d < bd: best, bd = j, d
        if best is None:
            best = min(big, key=lambda j: np.hypot(st[j, 0] + st[j, 2] / 2 - cx, st[j, 1] + st[j, 3] / 2 - cy))
        owner[i] = best
    out = []
    for li, L in enumerate(lines):
        bigs = L['m']
        core_line_top = int(np.median([st[i, 1] for i in L['m'] if i in big]))
        col = np.zeros(F.shape[1], bool)
        for i in bigs: col[st[i, 0]:st[i, 0] + st[i, 2]] = True
        # كلمات: فراغات أفقية بين المكوّنات الكبيرة لا تقل عن gap
        segs = []
        xs = np.nonzero(col)[0]
        start = xs[0]; prev = xs[0]
        for x in xs[1:]:
            if x - prev > gap: segs.append([start, prev]); start = x
            prev = x
        segs.append([start, prev])
        seg_of = {}
        for j in bigs:
            cx = st[j, 0] + st[j, 2] / 2
            seg_of[j] = int(np.argmin([0 if s[0] <= cx <= s[1] else min(abs(cx - s[0]), abs(cx - s[1])) for s in segs]))
        groups = [[] for _ in segs]
        for i in comps:
            if owner[i] not in seg_of: continue            # الحركة لسطر آخر
            if i in big: groups[seg_of[i]].append(i); continue
            cx = st[i, 0] + st[i, 2] / 2                    # الكلمة داخل السطر بموضعها الأفقي
            inside = [k for k, s in enumerate(segs) if s[0] - 3 <= cx <= s[1] + 3]
            if len(inside) == 1: groups[inside[0]].append(i); continue
            # بين كلمتين: تتبع الكلمة التي على يمينها (السابقة في القراءة)، كالفاصلة وضمة آخر الكلمة
            right = [(s[0] - cx, k) for k, s in enumerate(segs) if s[0] >= cx]
            if right: groups[min(right)[1]].append(i)
            else: groups[int(np.argmin([abs(cx - s[1]) for s in segs]))].append(i)
        for k in reversed(range(len(segs))):          # من اليمين
            g = groups[k]
            if not g: continue
            m = np.isin(lab, g)
            m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
            ys, xs2 = np.nonzero(m)
            X0, X1, Y0, Y1 = xs2.min(), xs2.max() + 1, ys.min(), ys.max() + 1
            out.append((F[Y0:Y1, X0:X1].copy(), (a * m)[Y0:Y1, X0:X1], (X0, Y0), li, core_line_top))
    return out, bg
