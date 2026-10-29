"""شرائح مدمجة للدرس الثاني: عدة صناديق من شرائح متتالية في شريحة واحدة بخطها الأصلي.

كل خطوة تُحفظ صورةً فيها العنوان وعنصر الخطوة وحده في موضعه الجديد، مع أقنعة عناصرها
(الصندوق، نصه، التظليل، السهم، أسطر الشرح) ليرسمها المحرك بالترتيب.
نص الشرح يُعاد لفّه كلمةً كلمة بكل حركاته (words.py).
"""
import os, sys, json, cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import words as WD

W, H = 1920, 1080
BOX = (600, 465, 1312, 690)        # الصندوق مع خط التظليل (هندسة واحدة في كل الشرائح)
ARROW = (944, 675, 976, 713)
TOP = 440                          # ما فوقه: اللافتة والعنوان


def page(n):
    F = cv2.imread(f'{S}/pages/{n:03d}.png')
    return np.vstack([F, F[-1:]])[:H]            # 1079 → 1080


def bg_color(F):
    return np.median(F[:40, :40].reshape(-1, 3), 0).astype(np.float32)


def alpha(img, bg):
    return np.clip(np.abs(img.astype(np.float32) - bg).max(2) / 120.0, 0, 1)


def paste(canvas, img, x, y, s, bg, opaque=False, mask=None):
    im = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s != 1 else img
    a = np.ones(im.shape[:2], np.float32) if opaque else alpha(im, bg)
    if mask is not None: a = cv2.resize(mask.astype(np.float32), (im.shape[1], im.shape[0]), interpolation=cv2.INTER_AREA) if s != 1 else mask
    h, w = im.shape[:2]
    reg = canvas[y:y + h, x:x + w].astype(np.float32)
    canvas[y:y + h, x:x + w] = (reg * (1 - a[..., None]) + im * a[..., None]).round().astype(np.uint8)
    return w, h


def wrap(wl, s, width, bg, gap=17):
    """يلف الكلمات (بحركاتها) في أسطر لا يتجاوز عرضها width، محاذاةً على أعلى جسم السطر."""
    items = []
    for im, a, (X0, Y0), li, ctop in wl:
        ims = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        als = cv2.resize(a, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        items.append((ims, als, (Y0 - ctop) * s))
    g = int(gap * s)
    # سطر قصير في الأصل (كالحكم «تقضيه») نهايته مقصودة: يبقى سطراً مستقلاً
    lw = {}
    for im, a, (X0, Y0), li, ctop in wl:
        lw.setdefault(li, [1e9, 0]); lw[li][0] = min(lw[li][0], X0); lw[li][1] = max(lw[li][1], X0 + a.shape[1])
    widths = {li: b - a for li, (a, b) in lw.items()}
    hard = {li for li, w in widths.items() if w < 0.6 * max(widths.values())}
    lines, cur, cw = [], [], 0
    prev_li = None
    for it, (_, _, _, li, _) in zip(items, wl):
        w = it[0].shape[1]
        if cur and (cw + g + w > width or (prev_li in hard and li != prev_li)): lines.append(cur); cur, cw = [], 0
        cw += (g if cur else 0) + w; cur.append(it); prev_li = li
    if cur: lines.append(cur)
    top = min(min(it[2] for it in ln) for ln in lines)
    step = int(max(it[0].shape[0] + it[2] for ln in lines for it in ln) - top + 4 * s)
    hgt = int(step * len(lines) + 10)
    out = np.full((hgt, width, 3), bg, np.uint8); oa = np.zeros((hgt, width), np.float32)
    line_masks = []
    for i, ln in enumerate(lines):
        tw = sum(it[0].shape[1] for it in ln) + g * (len(ln) - 1)
        x = (width + tw) // 2
        lm = np.zeros((hgt, width), np.float32)
        for ims, als, dy in ln:
            x -= ims.shape[1]
            y = int(round(i * step + dy - top))
            h, w = als.shape
            reg = (slice(y, y + h), slice(x, x + w))
            out[reg] = (out[reg] * (1 - als[..., None]) + ims * als[..., None]).astype(np.uint8)
            oa[reg] = np.maximum(oa[reg], als); lm[reg] = np.maximum(lm[reg], als)
            x -= g
        line_masks.append(lm)
    return out, oa, line_masks


def item(canvas, masks, n, cx, top, sb, sbody, width):
    """صندوق الشريحة n ونصه تحته، متمركزاً حول cx ومبتدئاً من top."""
    F = page(n); bg = bg_color(F)
    x0, y0, x1, y1 = BOX
    b = F[y0:y1, x0:x1].copy()
    wl, _ = WD.words(F, 712, 1075)
    if not wl:      # بلا نص تحته: يُمحى طرف السهم الداخل في قصاصة الصندوق
        b[ARROW[1] - y0:, ARROW[0] - x0:ARROW[2] - x0] = bg
    bw = int(round(b.shape[1] * sb)); bx = cx - bw // 2
    paste(canvas, b, bx, top, sb, bg, opaque=True)
    bh = int(round(b.shape[0] * sb))
    # أقنعة الصندوق من الصورة المصغّرة
    sm = cv2.resize(b, (bw, bh), interpolation=cv2.INTER_AREA).astype(int)
    B_, G_, R_ = sm[..., 0], sm[..., 1], sm[..., 2]
    blue = (B_ - R_ > 35) & (sm.max(2) - sm.min(2) > 30)
    yel = (R_ > 190) & (G_ > 160) & (R_ - B_ > 70)
    white = sm.min(2) > 247
    dark = (sm.max(2) < 150)
    def put(name, m):
        full = np.zeros((H, W), bool); full[top:top + bh, bx:bx + bw] = m; masks.setdefault(name, []).append(full)
    put('outline', blue); put('hl', yel); put('boxtext', dark & ~blue & ~yel)
    interior = np.zeros((H, W), bool)
    k, lab, st, _ = cv2.connectedComponentsWithStats((~blue).astype(np.uint8))
    put('boxfill', white | dark)
    bot = top + bh
    if wl:
        ax0, ay0, ax1, ay1 = ARROW
        arr = F[ay0:ay1, ax0:ax1].copy()
        aw = int(round((ax1 - ax0) * sb)); ay = bot - int(15 * sb)
        paste(canvas, arr, cx - aw // 2, ay, sb, bg)
        am = np.zeros((H, W), bool); ah = int(round((ay1 - ay0) * sb))
        sa = cv2.resize(arr, (aw, ah), interpolation=cv2.INTER_AREA).astype(int)
        am[ay:ay + ah, cx - aw // 2:cx - aw // 2 + aw] = (sa[..., 0] - sa[..., 2] > 25)
        masks.setdefault('arrow', []).append(am)
        body, ba, lms = wrap(wl, sbody, width, bg)
        y = ay + ah + 4
        paste(canvas, body, cx - width // 2, y, 1, bg, mask=ba)
        lines = []
        for lm in lms:
            full = np.zeros((H, W), bool); full[y:y + body.shape[0], cx - width // 2:cx - width // 2 + width] = lm > 0.06
            lines.append(full)
        masks.setdefault('lines', []).append(lines)
        bot = y + body.shape[0]
    else:
        masks.setdefault('arrow', []).append(np.zeros((H, W), bool)); masks.setdefault('lines', []).append([])
    return bot


def header(n):
    F = page(n); c = np.full_like(F, bg_color(F).astype(np.uint8)); c[:TOP] = F[:TOP]
    return c


def build(name, title_page, specs, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    full = header(title_page)
    info = []
    for k, (n, cx, top, sb, sbody, width) in enumerate(specs):
        st = header(title_page); masks = {}
        item(st, masks, n, cx, top, sb, sbody, width); item(full, {}, n, cx, top, sb, sbody, width)
        p = f'{out_dir}/{name}_{k + 1}.png'; cv2.imwrite(p, st)
        np.savez_compressed(f'{out_dir}/{name}_{k + 1}_masks.npz', **{kk: (v[0] if kk != 'lines' else np.array(v[0])) for kk, v in masks.items()})
        info.append(p)
    cv2.imwrite(f'{out_dir}/{name}_full.png', full)
    return info


if __name__ == '__main__':
    out = f'{HERE}/steps'
    R, L = 1410, 510
    sb, sv = 0.75, 0.75
    # الفرق بين قضاء الصلاة والصوم: الصوم (١) يميناً، والصلاة (٢) يساراً، بترتيب الكلام في الدرس
    print(build('farq', 52, [(53, R, 470, sb, sv, 840), (52, L, 470, sb, sv, 840)], out))
