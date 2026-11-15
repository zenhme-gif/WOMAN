"""شرائح الدرس الثاني بعد ورقة التعديل (40 شريحة): المنسوخة كما هي، والجديدة من الفيديو الجديد بطريقة extract.py نفسها
(إطار بلا يد، ولافتة ملونة من الإطار النهائي للمجموعة، وقرص الرقم مملوء)."""
import sys, os, json, shutil, subprocess, cv2, numpy as np
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
SRC = f'{S}/splice/lesson02_new.mp4'
OLD, OLD4 = f'{S}/slides/out_orig/درس2', f'{S}/hr/out_orig/درس2'
OUT, OUT4 = f'{S}/slides/out/درس2', f'{S}/hr/out/درس2'
W, H = 1920, 1080
PLATE = cv2.imread(f'{S}/l2/plate.png').astype(np.int16)
DISK_YEL = np.array([100, 211, 240], np.float32)


def frames(t0, t1, fps=10):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', SRC, '-vf', f'fps={fps}',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    n = len(r) // (W * H * 3)
    return [(t0 + i / fps, np.frombuffer(r[i * W * H * 3:(i + 1) * W * H * 3], np.uint8).reshape(H, W, 3).copy()) for i in range(n)]


def hand_px(f):
    g = f.astype(np.int16); d = np.abs(g - PLATE).max(2) > 40
    B, G, R = g[..., 0], g[..., 1], g[..., 2]
    skin = (d & (R > 140) & (R - B > 25) & (G * 100 > 55 * R) & (B * 100 > 45 * R)).astype(np.uint8)
    return int(cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)).sum())


def pick(t0, t1):
    c = [(hand_px(f), -t, t, f) for t, f in frames(t0, t1)]
    c.sort(key=lambda x: (x[0] > 1500, x[1]))      # بلا يد، وأحدثها
    h, _, t, f = c[0]
    return t, f, h


def unhand(f, page):
    """إن بقيت يد في الإطار: تُملأ مواضعها من الصفحة نفسها على اللوح (إحداثيات الصفحة 1080 = إحداثيات الإطار)."""
    g = f.astype(np.int16); d = np.abs(g - PLATE).max(2) > 40
    B, G, R = g[..., 0], g[..., 1], g[..., 2]
    skin = (d & (R > 140) & (R - B > 25) & (G * 100 > 55 * R) & (B * 100 > 45 * R)).astype(np.uint8)
    dark = (d & (np.abs(g - PLATE).max(2) > 90) & (g.max(2) < 120)).astype(np.uint8)       # القلم
    m = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    if m.sum() < 300: return f, 0
    m = cv2.dilate(m, np.ones((61, 61), np.uint8)) > 0
    m &= np.arange(H)[:, None] >= 400
    pg = cv2.imread(f'{S}/pages_edit/{page:03d}.png'); pg = np.vstack([pg, pg[-1:]])[:H]
    bgp = np.median(pg[:40, :40].reshape(-1, 3), 0)
    diff = np.abs(pg.astype(np.int16) - bgp).max(2) > 12
    comp = np.where(diff[..., None], pg, PLATE.astype(np.uint8))
    out = f.copy(); out[m] = comp[m]
    return out, int(m.sum())


def fill_disk(g):
    reg = g[380:520, 700:1220].astype(np.int16)
    B, G, R = reg[..., 0], reg[..., 1], reg[..., 2]
    yel = (R > 190) & (G > 160) & (R - B > 70)
    ys, xs = np.nonzero(yel)
    if len(ys) <= 50: return g
    cy, cx = ys.mean() + 380, xs.mean() + 700; rad = 38.5
    Y, X = np.mgrid[:H, :W]; dd = np.hypot(Y - cy, X - cx)
    gf = g.astype(np.float32); blue_target = np.array([123, 75, 7], np.float32)
    a = np.clip(((gf[..., 0] - gf[..., 2]) + 12) / 128.0, 0, 1); a[dd > rad - 3] = 0
    fill = DISK_YEL * (1 - a[..., None]) + blue_target * a[..., None]
    m3 = np.clip(rad + 0.5 - dd, 0, 1)[..., None]
    return np.clip(gf * (1 - m3) + fill * m3, 0, 255).astype(np.uint8)


# (رقم جديد، المصدر): رقم قديم للنسخ، أو ('box'|'final', نافذة البحث، صفحة، مجموعة)
FIN = {'n9': (370.0, 370.55), 'n14': (770.2, 770.85), 'n16': (899.8, 900.05)}
NEW = {14: ('box', (351.0, 357.0), 58, 'n9'), 15: ('final', FIN['n9'], 59, 'n9'),
       25: ('box', (744.0, 749.0) if False else (703.0, 708.2), 72, 'n14'), 26: ('final', FIN['n14'], 73, 'n14'),
       29: ('box', (862.0, 872.1), 77, 'n16'), 30: ('box', (884.0, 887.55), 78, 'n16'),
       31: ('box', (898.65, 898.95), 80, 'n16')}   # آخر «النفاس»: المحتوى قبل التلوين (اليد خارج الإطار)، واللافتة الملونة من النهاية
MAP = {}
for i in range(1, 14): MAP[i] = i
for i in range(16, 24): MAP[i] = i + 2
MAP[24] = 26
for i in (27, 28): MAP[i] = i + 3
for i in range(32, 41): MAP[i] = i + 4
if __name__ == '__main__':
    if not os.path.exists(OLD):
        shutil.copytree(OUT, OLD); shutil.copytree(OUT4, OLD4)
    for d in (OUT, OUT4):
        for f in os.listdir(d): os.remove(os.path.join(d, f))
    finals = {g: pick(*w)[1] for g, w in FIN.items()}
    log = []
    for k in range(1, 41):
        if k in MAP:
            shutil.copy(f'{OLD}/{MAP[k]:02d}.png', f'{OUT}/{k:02d}.png'); shutil.copy(f'{OLD4}/{MAP[k]:02d}.png', f'{OUT4}/{k:02d}.png')
            log.append(dict(k=k, old=MAP[k])); continue
        kind, win, page, grp = NEW[k]
        t, f, h = pick(*win)
        f, fixed = unhand(f, page)
        if kind == 'box':
            f[:390] = finals[grp][:390]; f = fill_disk(f)
        cv2.imwrite(f'{OUT}/{k:02d}.png', f, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        log.append(dict(k=k, kind=kind, page=page, t=round(t, 2), hand=h, unhand_px=fixed))
        print(k, kind, page, round(t, 2), 'hand', h, 'filled', fixed, flush=True)
    json.dump(log, open(f'{S}/slides/out/درس2_new.json', 'w'), ensure_ascii=False, indent=0)
