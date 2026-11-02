"""استخراج الشرائح كاملةً صوراً ثابتة من الدروس المنتَجة.

- نهاية كل مجموعة: حين تختفي اللافتة الحمراء (انتقال)؛ صورتها آخر إطار قبل ذلك بلا يد، وهي ملوّنة كاملة.
- المربعات داخل المجموعة: من مطابقة الصندوق بالصفحات الأصلية؛ صورة كل مربع آخر إطار قبل مسحه بلا يد،
  ويُكمَّل تلوينها (اللافتة من صورة المجموعة النهائية، وقرص الرقم يُملأ بالأصفر) لأن التلوين في الدرس يأتي آخر المجموعة.
الاستعمال: python3 extract.py رقم_الدرس
"""
import sys, os, json, subprocess, numpy as np, cv2

S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
K = int(sys.argv[1])
SRC = f'{S}/slides/l{K}.mp4'
INTRO_END = {1: 27.5, 2: 19.5, 3: 27.51, 4: 15.5}[K]
OUT = f'{S}/slides/out/درس{K}'
os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080
PLATE = cv2.imread(f'{S}/l2/plate.png').astype(np.int16)
DISK_YEL = np.array([100, 211, 240], np.float32)


def dur(p):
    import re
    o = subprocess.run(['ffmpeg', '-hide_banner', '-i', p], capture_output=True, text=True).stderr
    h, m, s = re.search(r'Duration: (\d+):(\d+):([\d.]+)', o).groups(); return int(h) * 3600 + int(m) * 60 + float(s)


MAIN_END = dur(SRC) - 5.77


def frames(t0, t1, fps=10):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{max(0, t0):.3f}', '-t', f'{t1 - t0:.3f}', '-i', SRC, '-vf', f'fps={fps}',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    n = len(r) // (W * H * 3)
    return [(max(0, t0) + i / fps, np.frombuffer(r[i * W * H * 3:(i + 1) * W * H * 3], np.uint8).reshape(H, W, 3)) for i in range(n)]


def corner(f):
    a = f[20:60, 20:60].reshape(-1, 3).astype(np.int16); b = f[600:640, 5:25].reshape(-1, 3).astype(np.int16)
    return float(np.median(np.vstack([a, b]), 0).sum())


def steady(fr):
    """يُستبعد ما كان في انتقال: الانتقال يعتم اللوح كله، فتقل الزاوية عن أنصع إطار في النافذة.
    (المقارنة نسبية لأن المقاطع المعاد ترميزها تختلف عن اللوح بدرجة أو درجتين.)"""
    if not fr: return fr
    cs = [corner(f) for _, f in fr]; cm = max(cs)
    return [x for x, c in zip(fr, cs) if c >= cm - 4]


def hand_px(f):
    g = f.astype(np.int16)
    d = np.abs(g - PLATE).max(2) > 40
    B, G, R = g[..., 0], g[..., 1], g[..., 2]
    skin = (d & (R > 140) & (R - B > 25) & (G * 100 > 55 * R) & (B * 100 > 45 * R)).astype(np.uint8)
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))   # تُزال حواف اللافتة والتظليل الرقيقة
    return int(skin.sum())


def red_px(f):
    g = f[150:420].astype(np.int16)
    return int(((g[..., 2] - g[..., 1] > 60) & (g[..., 2] - g[..., 0] > 60)).sum())


def low_ink(f):
    g = f[440:1060, 80:1840].astype(np.int16)
    return int((np.abs(g - PLATE[440:1060, 80:1840]).max(2) > 40).sum())


# 1) سلسلة اللافتة الحمراء (5 إطارات/ث بدقة مصغّرة)
def red_series():
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', SRC, '-vf', 'fps=5,scale=480:270', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                         stdout=subprocess.PIPE)
    out = []
    while True:
        b = p.stdout.read(480 * 270 * 3)
        if len(b) < 480 * 270 * 3: break
        g = np.frombuffer(b, np.uint8).reshape(270, 480, 3).astype(np.int16)[38:105]
        out.append(int(((g[..., 2] - g[..., 1] > 60) & (g[..., 2] - g[..., 0] > 60)).sum()))
    return np.array(out)


red = red_series(); FPS = 5
SCAN = np.load(f'{S}/slides/scan{K}.npz')
ends = []
for i in range(3, len(red) - 8):
    t = i / FPS
    if t < INTRO_END + 2 or t > MAIN_END - 1: continue
    pre = red[i - 3:i].max()
    # المجموعة لا تنتهي إلا بعد تلوين لافتتها كاملة (حدود اللافتة وحدها أقل من 1500 نقطة)
    if pre > 4000 and red[i] < 0.85 * pre and red[i:i + 8].min() < 0.1 * pre:
        if not ends or t - ends[-1] > 3: ends.append(t)
ends.append(MAIN_END)

# 2) مربعات من مطابقة الصفحات
m = json.load(open(f'{S}/slides/match{K}.json'))
runs = []
for t, n, sc in m:
    if sc < 0.75 or t < INTRO_END: continue
    if runs and runs[-1][1] == n and t - runs[-1][2] <= 3.0 and not any(runs[-1][2] < e < t for e in ends): runs[-1][2] = t
    else: runs.append([t, n, t])
runs = [r for r in runs if r[2] - r[0] >= 1.0]

items = []
g0 = INTRO_END
for gi, e in enumerate(ends):
    rs = [r for r in runs if g0 <= r[0] < e]
    for j, r in enumerate(rs[:-1]):
        if r[1] == rs[j + 1][1]: continue                   # المربع نفسه انقطعت مطابقته (اليد فوقه): يكفي آخر ظهور له
        items.append(dict(kind='box', group=gi, page=r[1], t0=r[0], t1=r[2], nxt=rs[j + 1][0], end=e))
    items.append(dict(kind='final', group=gi, page=rs[-1][1] if rs else None, t0=g0, end=e))
    g0 = e
print(f'L{K}: groups {len(ends)}, boxes {sum(1 for i in items if i["kind"] == "box")}, finals {sum(1 for i in items if i["kind"] == "final")}', flush=True)

# تصحيح اللون: المقاطع المعاد ترميزها أغمق بدرجات قليلة؛ يُعاد كل إطار إلى ألوان اللوح الأصلية
# بمطابقة خطية لكل قناة على حواف الإطار الثابتة (الشعارات والزخارف)
MARG = np.zeros((H, W), bool); MARG[:185] = True; MARG[:, :60] = True; MARG[:, 1860:] = True; MARG[1000:] = True


def normalize(f):
    g = f.astype(np.float32); P = PLATE.astype(np.float32); out = np.empty_like(g)
    m = MARG & (np.abs(g - P).max(2) < 25)
    for c in range(3):
        x = g[..., c][m]; y = P[..., c][m]
        A = np.vstack([x, np.ones_like(x)]).T
        a, b = np.linalg.lstsq(A, y, rcond=None)[0]
        out[..., c] = g[..., c] * a + b
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


# 3) اختيار الإطارات
def page_score(f, n):
    X0, Y0, X1, Y1 = 600, 490, 1312, 690
    nm = lambda g: (g.astype(np.float32) - g.mean()) / (g.std() + 1e-6)
    pg = cv2.imread(f'{S}/pages/{n:03d}.png'); pg = np.vstack([pg, pg[-1:]])
    a = nm(cv2.cvtColor(cv2.resize(pg[Y0:Y1, X0:X1], None, fx=0.5, fy=0.5), cv2.COLOR_BGR2GRAY))
    b = nm(cv2.cvtColor(cv2.resize(f[Y0:Y1, X0:X1], None, fx=0.5, fy=0.5), cv2.COLOR_BGR2GRAY))
    return float((a * b).mean())


finals = {}; extra = []
for it in items:
    if it['kind'] != 'final': continue
    fr = steady(frames(it['end'] - 3.0, it['end'] + 0.1, 15))
    free = [(t, f) for t, f in fr if hand_px(f) < 1500]            # الفرشاة حمراء: تُحسب اللافتة في الإطارات بلا يد فقط
    rmax = max([red_px(f) for _, f in free] or [0])
    ok = [(t, f) for t, f in free if red_px(f) >= 0.97 * rmax]
    if not ok: raise SystemExit(f"no hand-free final frame before {it['end']}")
    t, f = ok[-1]
    it['t'] = round(t, 2); it['hand'] = hand_px(f); finals[it['group']] = normalize(f)
    # آخر مربع مطابَق ليس هو ما في الصورة النهائية (تلته شريحة مدمجة): يُستخرج مربعاً مستقلاً
    rs = [r for r in runs if it['t0'] <= r[0] < it['end']]
    if rs and page_score(f, rs[-1][1]) < 0.6:
        extra.append(dict(kind='box', group=it['group'], page=rs[-1][1], t0=rs[-1][0], t1=rs[-1][2], nxt=it['end'] - 0.1, end=it['end']))
items += extra
# مربع لا يثبت على الشاشة إلا لحظة (كلام الشيخ متتابع) فلا يخلو له إطار من اليد: يؤخذ من حالة لوح المحرك بلا يد
INJECT = {2: [(59, 359.6, f'{S}/slides/p59_canvas.png')]}.get(K, [])
for n, t, src in INJECT:
    fin = next(i for i in items if i['kind'] == 'final' and i['t0'] <= t < i['end'])
    if any(i['kind'] == 'box' and i['page'] == n and i['group'] == fin['group'] for i in items): continue
    items.append(dict(kind='box', group=fin['group'], page=n, t0=t, t1=t, nxt=t, end=fin['end'], src=src))
for it in items:
    if it['kind'] != 'box': continue
    a = it['t1'] - 1.5; cand = [(it['t1'], cv2.imread(it.pop('src')))] if 'src' in it else []
    while not cand and a > it['t0'] - 1.5:                   # يُوسَّع البحث إلى الوراء حتى إطار بلا يد
        fr = frames(a, min(it['t1'] + 1.5, it['nxt']) if a == it['t1'] - 1.5 else a + 1.6, 10)
        cand = [(t, f) for t, f in steady(fr) if hand_px(f) < 1500]
        a -= 1.5
    if not cand: raise SystemExit(f"no hand-free frame for box page {it['page']} at {it['t1']}")
    best = max(low_ink(f) for _, f in cand)
    t, f = [c for c in cand if low_ink(c[1]) >= 0.97 * best][-1]
    it['t'] = round(t, 2); it['hand'] = hand_px(f)
    # إكمال التلوين: اللافتة من صورة المجموعة النهائية
    g = normalize(f); fin = finals[it['group']]
    g[:400] = fin[:400]
    # قرص الرقم: حلقة صفراء فوق الصندوق تُملأ بالأصفر ويُحفظ الرقم
    reg = g[380:520, 700:1220].astype(np.int16)
    B, G, R = reg[..., 0], reg[..., 1], reg[..., 2]
    yel = (R > 190) & (G > 160) & (R - B > 70)
    ys, xs = np.nonzero(yel)
    if len(ys) > 50:
        cy, cx = ys.mean() + 380, xs.mean() + 700
        rad = 38.5
        Y, X = np.mgrid[:H, :W]
        dd = np.hypot(Y - cy, X - cx)
        gf = g.astype(np.float32)
        blue_target = np.array([123, 75, 7], np.float32)
        # شدة الرقم من زرقته وحدها (الحلقة الصفراء ليست زرقاء): B−R من −12 على اللوح إلى 116 في الرقم
        a = np.clip(((gf[..., 0] - gf[..., 2]) + 12) / 128.0, 0, 1)
        a[dd > rad - 3] = 0
        fill = DISK_YEL * (1 - a[..., None]) + blue_target * a[..., None]
        m3 = np.clip(rad + 0.5 - dd, 0, 1)[..., None]
        gf = gf * (1 - m3) + fill * m3
        g = np.clip(gf, 0, 255).astype(np.uint8)
        it['disk'] = (round(float(cx)), round(float(cy)))
    it['img'] = g
# 4) الحفظ بترتيب الظهور
items.sort(key=lambda i: i['t'])
log = []
for k, it in enumerate(items, 1):
    img = it.pop('img', None)
    if img is None: img = finals[it['group']]
    name = f'{OUT}/{k:02d}.png'
    cv2.imwrite(name, img, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    log.append({kk: (vv if not isinstance(vv, np.generic) else vv.item()) for kk, vv in it.items()})
json.dump(log, open(f'{S}/slides/out/درس{K}.json', 'w'), ensure_ascii=False, indent=0)
print(f'L{K}: saved {len(items)} slides; max hand px {max(i["hand"] for i in log)}', flush=True)
