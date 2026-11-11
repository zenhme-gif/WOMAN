"""رسم جزئي: من لحظة Ts (قبل كتابة الشرح المعدّل) إلى نهاية المجموعة B.
ما قبل Ts يبقى من الأصل. اللوح عند Ts يُبنى من إطار بلا يد بعد الكتابة، ويُمحى منه الشرح القديم؛
والقلم يبدأ من موضعه في الأصل عند Ts فلا يقفز."""
import sys, subprocess, cv2, numpy as np
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
sys.path.insert(0, f'{S}/r2'); sys.path.insert(0, f'{S}/txt'); sys.path.insert(0, f'{S}/regroup')
import render2 as R, slide_edit as SE, steps_from_slide as SF
W, H = 1920, 1080


def frame(v, t):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.4f}', '-i', v, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(H, W, 3).copy()


def clean_board(v, t_free, box, cy_rng):
    """إطار بلا يد، وقد مُحي منه حبر الشرح القديم في box بخلفيته المرمّمة."""
    F = frame(v, t_free)
    out, ink = SE.apply(F, box, lambda a, x0: [], cy_rng)
    return out, ink


def find_tip(F, board, hand='pen'):
    """موضع رأس الأداة في الإطار F فوق اللوح board: تقدير من حافة اليد اليسرى ثم بحث دقيق بالمطابقة."""
    hd = R.HANDS[hand]; tx, ty = hd['tip']
    d = np.abs(F.astype(np.int16) - board.astype(np.int16)).max(2) > 40
    d = cv2.morphologyEx(d.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(d)
    if n < 2: return None
    j = 1 + np.argmax(st[1:, 4]); m = lab == j
    ys, xs = np.nonzero(m); x0 = xs.min(); y_at = int(np.median(ys[xs <= x0 + 2]))
    al = hd['alpha'] > 0.5; sy, sx = np.nonzero(al); smin = sx.min(); sy_at = int(np.median(sy[sx <= smin + 2]))
    cx, cy = x0 + (tx - smin), y_at + (ty - sy_at)
    y0b, y1b, x0b, x1b = max(0, ys.min() - 20), min(H, ys.max() + 20), max(0, xs.min() - 20), min(W, xs.max() + 20)
    Ff = F[y0b:y1b, x0b:x1b].astype(np.float32)
    def err(px, py):
        fr = board.astype(np.float32).copy(); R.place_hand(fr, hand, (px, py))
        return float(np.abs(fr[y0b:y1b, x0b:x1b] - Ff).mean())
    best = (err(cx, cy), cx, cy)
    for step, rad in ((4, 24), (1, 4)):
        bx, by = best[1], best[2]
        for dy in range(-rad, rad + 1, step):
            for dx in range(-rad, rad + 1, step):
                e = err(bx + dx, by + dy)
                if e < best[0]: best = (e, bx + dx, by + dy)
    return np.array([best[1], best[2]], np.float32), best[0]


def disks_of(slide):
    """أقراص الترقيم الصفراء (مركز ونصف قطر) في شريحة 1080."""
    f = slide.astype(int); B, G, Rr = f[..., 0], f[..., 1], f[..., 2]
    yel = (Rr > 190) & (G > 160) & (Rr - B > 70); yel[:385] = False
    n, lab, st, c = cv2.connectedComponentsWithStats(yel.astype(np.uint8))
    out = []
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if 50 < w < 100 and 0.8 < w / h < 1.25 and a > 1500: out.append((x + w / 2, y + h / 2, w / 2))
    return out


def disk_fill(slide, cx, cy, r):
    Y, X = np.mgrid[:H, :W]; m = np.hypot(Y - cy + 0.5, X - cx + 0.5) <= r + 1.5
    return R.spiral_fill(m, slide.astype(np.float32))


def hand_mask(pos, hand='pen', grow=4):
    """ما تغطيه اليد وظلها في الإطار إذا كان رأسها عند pos."""
    one = np.ones((H, W, 3), np.float32) * 100
    fr = one.copy(); R.place_hand(fr, hand, pos)
    m = (np.abs(fr - one).max(2) > 0.3).astype(np.uint8)
    return cv2.dilate(m, np.ones((2 * grow + 1, 2 * grow + 1), np.uint8)) > 0


def board_at(F_ts, tip, board_free, hand='pen'):
    """اللوح عند Ts: الإطار الأصلي نفسه خارج اليد، واللوح النظيف تحتها."""
    m = hand_mask(tip, hand)
    out = F_ts.copy(); out[m] = board_free[m]
    return out
