"""إعادة بناء إطارات الدرس بدقة 3840×2160: كل نقطة في الإطار تطابق طبقةً معروفة (اللوح، أو الشريحة مكتملةً
أو قبل تلوينها) تؤخذ من نسختها العالية الدقة، وما سواها (اليد ورأس القلم وأثناء الانتقال) يُكبَّر من الإطار نفسه.
الاستعمال: python3 compose.py K SRC n0 n1 OUT"""
import sys, subprocess, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/v4k')
import layers as L
cv2.setNumThreads(1)                                   # ثلاث عمليات متوازية على أربع نوى: لا تزاحم خيوط
S = L.S
k, SRC, n0, n1, OUT = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
FPS, W, H = 30, 1920, 1080
INTRO_END = {1: 27.5, 2: 19.5, 3: 27.51, 4: 15.5}[k]
import os; INTRO_INK = int(os.environ.get('INTRO_INK', 40))
DUR = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC], capture_output=True, text=True).stdout)
OUTRO = DUR - 5.77
TOL = 24
ITEMS = L.items(k)
for i, it in enumerate(ITEMS): it['idx'] = i + 1
GROUPS = sorted({it['group'] for it in ITEMS})
G = {g: [it for it in ITEMS if it['group'] == g] for g in GROUPS}
GT = {g: (min(it['t0'] for it in G[g] if it['kind'] == 'final'), max(it['end'] for it in G[g])) for g in GROUPS}
blur = lambda x: cv2.GaussianBlur(x, (0, 0), 1.0)
PLATE4 = L.PLATE4; PL1b = cv2.GaussianBlur(L.PLATE1, (0, 0), 1.0)
_cache = {}


def layer_set(t):
    """الطبقات المحتملة عند الزمن t: شرائح المجموعة الحالية (والسابقة أول ثلاث ثوانٍ)."""
    if t < INTRO_END:
        key = ('intro',)
        if key not in _cache:
            P4 = cv2.imread(f'{S}/hr/pages4k/001.png').astype(np.float32)
            # خلفية الغلاف بلون الصفحة (234،239،242) أفتح من لوح الفيديو (228،236،240): تُعاد إلى لون اللوح، والحبر كما هو
            cpg = np.array([234, 239, 242], np.float32); cpl = np.array([228, 236, 240], np.float32)
            a = np.clip(np.abs(P4 - cpg).max(2) / 60.0, 0, 1)[..., None]
            P4 = np.clip(P4 + (cpl - cpg) * (1 - a) + 0.5, 0, 255).astype(np.uint8)
            d1 = cv2.resize(P4, (W, H), interpolation=cv2.INTER_AREA)
            _cache.clear(); _cache[key] = [(P4, blur(d1), maxdiff(d1, L.PLATE1) > INTRO_INK)]   # العلامة المائية الباهتة في الغلاف حبرٌ لا يظهر قبل أن يُكتب
        return key, _cache[key]
    if t >= OUTRO: return ('outro',), []
    gs = [g for g in GROUPS if GT[g][0] <= t < GT[g][1]] or [GROUPS[-1]]
    g = gs[0]
    use = [g] + ([GROUPS[GROUPS.index(g) - 1]] if GROUPS.index(g) > 0 and t - GT[g][0] < 3 else [])
    key = tuple(use)
    if key not in _cache:
        old = {kk: v for kk, v in _cache.items() if kk != ('intro',)}
        lay = []
        for gg in use:
            for it in G[gg]:
                ck = ('item', it['idx'])
                pair = None
                for kk, v in old.items():
                    pass
                f4, u4 = L.item_layers(k, it['idx'], it)
                for x4 in (u4, f4):
                    d1 = cv2.resize(x4, (W, H), interpolation=cv2.INTER_AREA)
                    lay.append((x4, blur(d1), maxdiff(d1, L.PLATE1) > 40))
        _cache.clear(); _cache[key] = lay
    return key, _cache[key]


def maxdiff(a, b):
    d = cv2.absdiff(a, b); c = cv2.split(d)
    return cv2.max(cv2.max(c[0], c[1]), c[2])


def compose_region(F, out4, lay, y0, y1, x0, x1):
    M = 6
    ym0, ym1, xm0, xm1 = max(0, y0 - M), min(H, y1 + M), max(0, x0 - M), min(W, x1 + M)
    Fb = cv2.GaussianBlur(F[ym0:ym1, xm0:xm1], (0, 0), 1.0)[y0 - ym0:y1 - ym0, x0 - xm0:x1 - xm0]
    dp = maxdiff(Fb, PL1b[y0:y1, x0:x1])
    if lay:
        # حبر في الطبقة لا يقابله حبر في الإطار (لم يُرسم بعد): تُرفض الطبقة هناك، فلا يظهر طيف لما لم يُكتب
        inkF = cv2.dilate((maxdiff(F[y0:y1, x0:x1], L.PLATE1[y0:y1, x0:x1]) > 25).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        D = []
        for _, l1, ink in lay:
            d = maxdiff(Fb, l1[y0:y1, x0:x1])
            bad = cv2.dilate((ink[y0:y1, x0:x1] & ~inkF).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            d[bad] = 255; D.append(d)
        D = np.stack(D)
        best = D.min(0); bestk = D.argmin(0)
        acc = best < TOL
        acc = cv2.morphologyEx(acc.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0   # لا قطع رفيعة من الأصل وسط المكبَّر
        grow = (cv2.dilate(acc.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0) & (best < 2 * TOL)
        acc |= grow
    else:
        acc = np.zeros(dp.shape, bool); bestk = None
    pl = ~acc & (dp < TOL)
    Y0, Y1, X0, X1 = 2 * y0, 2 * y1, 2 * x0, 2 * x1
    sz = (X1 - X0, Y1 - Y0)
    reg = out4[Y0:Y1, X0:X1]
    reg[:] = cv2.resize(F[y0:y1, x0:x1], sz, interpolation=cv2.INTER_CUBIC)
    fbm = ~acc & ~pl
    near = cv2.dilate(fbm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    pl = pl & ~near                                            # حول ما يُكبَّر من الإطار: انتقال ناعم لا قطع
    def blend(src, m):
        w = cv2.resize(m.astype(np.float32), sz, interpolation=cv2.INTER_LINEAR)
        w = cv2.GaussianBlur(w, (0, 0), 0.8)
        full = w > 0.999; part = (w > 0.001) & ~full
        cv2.copyTo(src, full.astype(np.uint8), reg)
        if part.any():
            ww = w[part][:, None]; reg[part] = (src[part] * ww + reg[part] * (1 - ww) + 0.5).astype(np.uint8)
    if pl.any(): blend(PLATE4[Y0:Y1, X0:X1], pl)
    if acc.any():
        for i in np.unique(bestk[acc]):
            blend(lay[i][0][Y0:Y1, X0:X1], acc & (bestk == i))
    return float((~acc & ~pl).mean())


dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', f'{n0 / FPS:.6f}', '-i', SRC, '-frames:v', str(n1 - n0), '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '3840x2160', '-r', str(FPS), '-i', '-',
                        '-sws_flags', 'accurate_rnd+full_chroma_int+bitexact', '-c:v', 'libx264', '-preset', 'faster', '-crf', '20', '-threads', '2', '-pix_fmt', 'yuv420p',
                        '-video_track_timescale', '15360', OUT], stdin=subprocess.PIPE)
# نقاط خلفية خالصة في الحواف: إن ابتعد لونها عن اللوح فالإطار في انتقال (خفوت عام) فيُكبَّر كله من الإطار نفسه
_m = np.zeros((H, W), bool); _m[2:30, 300:1500] = True; _m[1052:1078, 300:1500] = True
SAMP = _m & (np.abs(L.PLATE1.astype(np.int16) - np.array([228, 236, 240])).max(2) <= 1)
def in_fade(F):
    return float(np.median(np.abs(F[SAMP].astype(np.int16) - L.PLATE1[SAMP].astype(np.int16)).max(1))) >= 3
out4 = np.zeros((2160, 3840, 3), np.uint8); prevF = None; prevkey = None; nf = 0; soft = []
import time; T0 = time.time()
for n in range(n0, n1):
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    F = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    t = n / FPS
    key, lay = layer_set(t)
    if key == ('outro',) or in_fade(F):
        out4 = cv2.resize(F, (3840, 2160), interpolation=cv2.INTER_CUBIC); prevF = None; prevkey = key
    else:
        # يُقارن الإطار بآخر حالة رُسمت فعلاً (لا بالإطار السابق)، فالتغيّر البطيء في الانتقال يُلتقط ولا يبقى أثر قديم
        if prevF is None or key != prevkey:
            soft.append(compose_region(F, out4, lay, 0, H, 0, W)); prevF = F.copy()
        else:
            ch = maxdiff(F, prevF) > 6
            if ch.any():
                ch = cv2.dilate(ch.astype(np.uint8), np.ones((9, 9), np.uint8))
                x, y, w, h = cv2.boundingRect(cv2.findNonZero(ch))
                y0, y1, x0, x1 = max(0, y - 4), min(H, y + h + 4), max(0, x - 4), min(W, x + w + 4)
                soft.append(compose_region(F, out4, lay, y0, y1, x0, x1))
                prevF[y0:y1, x0:x1] = F[y0:y1, x0:x1]
        prevkey = key
    enc.stdin.write(out4.tobytes()); nf += 1
    if nf % 300 == 0: print(f'{nf} frames, {nf / (time.time() - T0):.1f} fps', flush=True)
enc.stdin.close(); enc.wait(); dec.wait()
print('done', OUT, nf, 'frames', f'{time.time() - T0:.0f}s', 'mean soft share of recomputed regions %.3f' % (np.mean(soft) if soft else 0), flush=True)
