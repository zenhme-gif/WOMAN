"""إعادة رسم مجموعة كاملة (لافتة وصناديقها) من صفحات معدّلة، بتوقيت مقيس من الفيديو الأصلي.
المقطع [A, B]: من فراغ اللوح قبل المجموعة إلى فراغه بعدها."""
import sys, os, subprocess, cv2, numpy as np, json
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
sys.path.insert(0, f'{S}/r2')
import render2 as R
W, H, FPS = 1920, 1080, 30


def thin_highlight(F):
    """شريط التظليل في الصفحة سميك (26 نقطة)، وفي الفيديو المنتج خط رفيع (4 نقاط) عند منتصفه: يُوحَّد على الفيديو."""
    f = F.astype(int); B, G, R = f[..., 0], f[..., 1], f[..., 2]
    yel = (R > 190) & (G > 160) & (R - B > 70); yel[:440] = False
    n, lab, st, _ = cv2.connectedComponentsWithStats(yel.astype(np.uint8))
    bg = np.median(F[:40, :40].reshape(-1, 3), 0)
    col = np.median(F[yel].reshape(-1, 3), 0) if yel.any() else None
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if not (18 <= h <= 34 and w > 120): continue
        F[lab == j] = bg
        y0 = y + 12
        for dy, al in ((0, 0.45), (1, 0.7), (2, 1.0), (3, 1.0)):
            F[y0 + dy, x:x + w] = np.round(F[y0 + dy, x:x + w] * (1 - al) + col * al).astype(np.uint8)
    return F


def page1080(n):
    p = f'{S}/pages_edit/{n:03d}.png'
    F = cv2.imread(p if os.path.exists(p) else f'{S}/pages/{n:03d}.png')
    return thin_highlight(np.vstack([F, F[-1:]])[:H])


def frames(video, t0, t1, scale=1):
    w, h = W // scale, H // scale
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t0:.4f}', '-i', video, '-t', f'{t1 - t0:.4f}', '-vf', f'scale={w}:{h}' if scale > 1 else 'null',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(-1, h, w, 3)


def build(pages, step_imgs=None, disk_r=38):
    imgs = step_imgs or [page1080(n) for n in pages]
    bg = np.median(imgs[0][:40, :40].reshape(-1, 3), 0).astype(np.float32)
    hd = R.Header(imgs[0], bg)
    its = [R.Item(im, bg, k + 1, disk_r=disk_r) for k, im in enumerate(imgs)]
    return hd, its


def measure(video, A, B, items):
    """زمن بدء رسم العنوان، وزمن ظهور حلقة كل قرص (بدء كل صندوق). الإطارات تُقرأ تباعاً بلا تخزين."""
    PL = R.PLATE.astype(np.int16)
    boxes = []
    for it in items:
        ys, xs = np.nonzero(it.disk); cy, cx = int(ys.mean()), int(xs.mean()); r = int(np.ptp(xs) / 2) + 4
        boxes.append((cy, cx, r))
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{A:.4f}', '-i', video, '-t', f'{B - A:.4f}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    tc, rc = [], [[] for _ in items]
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        tc.append(int((np.abs(f[150:430, 300:1620].astype(np.int16) - PL[150:430, 300:1620]).max(2) > 40).sum()))
        for k, (cy, cx, r) in enumerate(boxes):
            sub = f[cy - r:cy + r, cx - r:cx + r].astype(np.int16)
            rc[k].append(int(((sub[..., 2] > 200) & (sub[..., 1] > 180) & (sub[..., 0] < 135) & (sub[..., 2] - sub[..., 0] > 95)).sum()))
    p.wait()
    tcount = np.array(tc)
    t_title = A + int(np.argmax(tcount > 150)) / FPS
    starts = []; i_prev = 0
    for k in range(len(items)):
        c = np.array(rc[k]); on = np.nonzero(c[i_prev:] > 25)[0]
        if not len(on): starts.append(None); continue
        i = i_prev + on[0]; starts.append(A + i / FPS)
        # الحلقة التالية في الموضع نفسه تظهر بعد مسح هذه: غياب متصل ثلث ثانية على الأقل
        lowrun = np.convolve((c[i:] <= 5).astype(int), np.ones(10, int), 'valid')
        off = np.nonzero(lowrun == 10)[0]
        i_prev = i + (off[0] if len(off) else 30)
    return t_title, starts, tcount


def plan(header, items, A, B, t_title, starts, keep, fade_start):
    """الرسم حتى بدء انتقال الأصل، ثم انتقال ينتهي عند B كما في الأصل."""
    tl = R.Timeline(A)
    R.plan_group(tl, header, items, [s + 0.3 for s in starts], fade_start, keep=keep, next_exists=False, title_at=t_title + 0.2)
    tl.leave()
    f0 = max(tl.t, fade_start)
    if f0 > fade_start + 0.25: print('  تنبيه: انتهى الرسم بعد بدء انتقال الأصل بـ', round(f0 - fade_start, 2), 'ث')
    f0 = min(f0, B - 0.35)
    tl.ev.append(('fade', f0, B)); tl.t = B
    return tl


if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1]))
    hd, its = build(cfg['pages'], disk_r=cfg.get('disk_r', 38))
    t_title, starts, _ = measure(cfg['video'], cfg['A'], cfg['B'], its)
    print('title', round(t_title, 2), 'starts', [round(s, 2) for s in starts], flush=True)
    tl = plan(hd, its, cfg['A'], cfg['B'], t_title, starts, cfg.get('keep', False), cfg['F'])
    R.render(tl.ev, cfg['A'], cfg['B'], cfg['out'])
    print('done', cfg['out'], 'timeline end', round(tl.t, 2))
