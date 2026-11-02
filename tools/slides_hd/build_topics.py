"""شرائح «موضوعات الدرس» بدقة 4K: الصناديق والتظليل واللافتة من الصفحات الأصلية (بمقياسها)،
والنصوص تُعاد كتابتها بخط تجوّل (Tajawal) بالمقاس والموضع المطابقين للشريحة."""
import cv2, numpy as np, json, sys, os
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/hr')
import build_std as B, build_comp as C
S = B.S; FONT = B.FONT
TEXTS = {
    '1': ["اشتراك الرجال والنساء", "في الأحكام الشرعية", "تخصيص النساء", "بالتعليم الشرعي", "حكم ما يوضع على البشرة", "عند الوضوء والغسل",
          "أثر استعمال الكريمات", "في الوضوء والغسل", "صفة مسح", "المرأة رأسها", "من أحكام مسح الرأس", "حكم مسح المرأة", "على الخمار",
          "من ضوابط", "المسح على الخمار", "وضوء المرأة", "عند تنجية ولدها", "إصابة المتوضئ نجاسة", "على بدنه أو ثوبه", "خروج الريح من المرأة",
          "مس الرجل والمرأة", "وأثره على الوضوء", "نقض المرأة", "شعرها عند الغسل", "التطيب بعد", "الاغتسال من الحيض"],
    '2': ["ما يحرم بالحيض", "والنفاس", "الطهر قبل", "الفجر في رمضان", "بمَ يحصل الطهر", "من الحيض", "الصفرة والكدرة", "زمن الحيض وبعده",
          "الدم النازل من", "المرأة بعد الخمسين", "الدم الذي ينزل", "من الحامل", "حكم استعمال", "حبوب منع الحيض", "أكثر مدة النفاس",
          "المرأة بعد الإسقاط", "حكم الإجهاض"],
    '3': ["وجوب محافظة المرأة", "على الصلوات الخمس", "مراعاة المرأة", "الطمأنينة في صلاتها", "أمر الأم أولادها بالصلاة", "مواقيت الصلوات",
          "الخمس", "عورة المرأة في الصلاة", "الصلاة باللثام", "على الفم والأنف"],
    '4': ["حكم الأذان", "والإقامة للنساء", "صلاة المرأة مع", "الجماعة في المسجد", "عدم مخالطة النساء", "الرجال في المسجد",
          "إمامة المرأة في الصلاة", "موقف المرأة في", "صلاة الجماعة"],
}
HEADER = "موضوعات الدرس"
_r = {}


def render4(text, size):
    """النص بدقة 4K: صورة ألفا مقصوصة على حدود الحبر، وإزاحتها من نقطة الرسم."""
    k = (text, size)
    if k not in _r:
        f = ImageFont.truetype(FONT, size)
        l, t, r, b = f.getbbox(text, direction='rtl', language='ar') if hasattr(f, 'getbbox') else (0, 0, 0, 0)
        im = Image.new('L', (int(r - l) + 20, int(b - t) + 20), 0)
        ImageDraw.Draw(im).text((10 - l, 10 - t), text, font=f, fill=255, direction='rtl', language='ar')
        a = np.asarray(im).astype(np.float32) / 255
        ys, xs = np.nonzero(a > 0.02)
        _r[k] = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return _r[k]


def fit_line(s1g, box, texts, dark):
    """أي النصوص وبأي مقاس يطابق سطر الشريحة: يُرسم بدقة 4K ويُصغَّر ويُقارن."""
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    crop = s1g[max(0, y0 - 6):y1 + 6, max(0, x0 - 6):x1 + 6]
    best = None
    for t in texts:
        # المقاس الذي يجعل عرض الحبر في 4K ضعف عرضه في الشريحة
        lo, hi = 20, 160
        while lo < hi:
            mid = (lo + hi) // 2
            if render4(t, mid).shape[1] < 2 * w: lo = mid + 1
            else: hi = mid
        for size in (lo - 1, lo, lo + 1):
            a = render4(t, size)
            sm = cv2.resize(a, (max(1, round(a.shape[1] / 2)), max(1, round(a.shape[0] / 2))), interpolation=cv2.INTER_AREA)
            tmpl = 255 - sm * (255 - dark)                     # نص داكن على فاتح
            if tmpl.shape[0] > crop.shape[0] or tmpl.shape[1] > crop.shape[1]: continue
            m = cv2.matchTemplate(crop, tmpl.astype(np.float32), cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(m)
            if best is None or mx > best[0]: best = (mx, t, size, loc[0] + max(0, x0 - 6), loc[1] + max(0, y0 - 6))
    return best


def build(k):
    s1 = cv2.imread(f'{S}/slides/out/درس{k}/{"05" if k == "1" else "01"}.png')
    f = s1.astype(np.int16)
    PL1 = C.PL1.astype(np.int16)
    blue = (f[..., 0] - f[..., 2] > 30)
    # نص الصناديق الداكن، ونص اللافتة الأبيض
    dark = (f.max(2) < 150) & ~blue; dark[:420] = False; dark[1015:] = False
    red = (f[..., 2] > 150) & (f[..., 2] - f[..., 0] > 60) & (f[..., 2] - f[..., 1] > 50)
    from scipy import ndimage as ndi
    nr, lr, sr, _ = cv2.connectedComponentsWithStats(red.astype(np.uint8)); jb = 1 + int(np.argmax(sr[1:, 4]))
    ban = ndi.binary_fill_holes(lr == jb)
    white = (cv2.erode(ban.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0) & (f.min(2) > 150)
    # الشريحة بلا نصوص: تُبنى صناديقها ولافتتها بالمطابقة
    clean = s1.copy()
    bl2 = (f[..., 0] - f[..., 2] > 25) & (f.max(2) - f.min(2) > 25)
    yl2 = (f[..., 2] > 180) & (f[..., 1] > 150) & (f[..., 2] - f[..., 0] > 40)
    mo = cv2.morphologyEx((bl2 | yl2).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)); mo[:420] = 0
    inner = ndi.binary_fill_holes(mo > 0) & ~(mo > 0)
    inner = cv2.erode(inner.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0       # داخل الصناديق (النص وحده)
    clean[inner] = C.PL1[inner]
    dark &= inner | (cv2.dilate(inner.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    redc = np.median(s1[lr == jb].reshape(-1, 3), 0).astype(np.uint8)
    wd = (cv2.dilate(white.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0) & ban
    clean[wd] = redc
    log = []
    img, stats, todo = C.build(clean, [12, 13, 44, 92, 120, 131], [1.0], log, hl=False)
    print(k, 'boxes', stats, flush=True)
    # الأسطر
    g = cv2.cvtColor(s1, cv2.COLOR_BGR2GRAY).astype(np.float32)
    dark_v = float(np.percentile(g[dark], 5))
    lines = []
    n, lab, st, _ = cv2.connectedComponentsWithStats(cv2.dilate(dark.astype(np.uint8), np.ones((5, 23), np.uint8)))
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if a < 1200: continue
        mm = (lab == j) & dark; ys, xs = np.nonzero(mm)
        lines.append((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    texts = TEXTS[k]
    color = np.median(s1[dark & (g < dark_v + 25)].reshape(-1, 3), 0)
    rep = []
    for bx in sorted(lines, key=lambda b: (b[1] // 40, -b[0])):
        r = fit_line(g, bx, texts, dark_v)
        if r is None: print('  no fit for line', bx, flush=True); continue
        sc, t, size, x, y = r
        a = render4(t, size)
        X, Y = 2 * x, 2 * y
        reg = img[Y:Y + a.shape[0], X:X + a.shape[1]]
        reg[:] = color * a[..., None] + reg * (1 - a[..., None])
        rep.append((t, size, round(float(sc), 3)))
    # العنوان الأبيض
    ys, xs = np.nonzero(white)
    hb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    inv = 255 - g
    sc, t, size, x, y = fit_line(inv, hb, [HEADER], 255 - float(np.percentile(g[white], 95)))
    a = render4(t, size); X, Y = 2 * x, 2 * y
    wcol = np.median(s1[white & (g > np.percentile(g[white], 60))].reshape(-1, 3), 0)
    reg = img[Y:Y + a.shape[0], X:X + a.shape[1]]; reg[:] = wcol * a[..., None] + reg * (1 - a[..., None])
    rep.append((t, size, round(float(sc), 3)))
    mean, bad = B.verify(img, s1)
    i = "05" if k == "1" else "01"
    cv2.imwrite(f'{S}/hr/out/درس{k}/{i}.png', np.clip(img + 0.5, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 6])
    used = [r[0] for r in rep[:-1]]
    print(k, 'verify mean %.2f bad %d' % (mean, bad), 'lines', len(lines), 'unused', [t for t in texts if t not in used], flush=True)
    for r in rep: print('  ', r)


if __name__ == '__main__':
    for k in sys.argv[1:]: build(k)
