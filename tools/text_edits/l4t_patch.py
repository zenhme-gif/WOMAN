"""الدرس الرابع، موضوعات الدرس: إحلال نص المربع الأول الجديد «أذان المرأة / وإقامتها» في إطارات الفيديو (1080).
طوران: (1) الكتابة (قبل الإطار 569): النص في الأصل طبقة عليا تُكتب فوق اليد، من اليمين لليسار وتختفي وتعود؛
    فتُقاس عتامته لكل شريحة عرضها 8 بكسلات من مطابقة لون الحبر، ويُرمَّم ما تحته، ويُرسم الجديد بالعتامة نفسها.
(2) بعده: النص تحت اليد. يُقاس فرق الحبر عن اللوح لكل قناة ولكل سطر (يشمل التلاشي)، وتُعاد كتابة منطقة النص
    من لون اللوح والنص الجديد حيث لا يد، مع الظل؛ وما بقي من حبر قديم ملاصق لحافة اليد يُرمَّم."""
import sys, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
Y0, Y1, X0, X1 = 440, 528, 1446, 1666
SPLIT = 482                                            # بين السطرين (1080)
# ألفا النص القديم ولون حبره وخلفيته من متوسط 70 إطاراً نظيفاً من الفيديو نفسه (19.17–21.5 ث)، لا من الشريحة
AVG = np.load(f'{S}/txt/l4t_avg.npy')[Y0 - 430:Y1 - 430, X0 - 1436:X1 - 1436]
_L = AVG.mean(2)
INKV = np.median(AVG[_L < np.percentile(_L, 2)].reshape(-1, 3), 0).astype(np.float32)
_a0 = np.clip((np.median(AVG[_L > np.percentile(_L, 60)].reshape(-1, 3), 0).mean() - _L) / 150, 0, 1)
_near = cv2.dilate((_a0 > 0.12).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
_far = ~(cv2.dilate(_near.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
BG = np.median(AVG[_far].reshape(-1, 3), 0).astype(np.float32)
D_REF = (INKV - BG).astype(np.float32)
A_old = np.clip(((AVG - BG) @ D_REF) / (D_REF @ D_REF), -0.5, 1.0).astype(np.float32)
A_old[~_near] = 0
A_new = np.load(f'{S}/txt/l4t_a1.npy')[Y0:Y1, X0:X1]
strong = A_old > 0.8
near_any = cv2.dilate(((np.abs(A_old) > 0.02) | (A_new > 0.02)).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
far = ~near_any
bgish_nb = cv2.blur((np.abs(A_old) < 0.05).astype(np.float32), (7, 7))
rows = np.arange(Y1 - Y0)[:, None] + Y0
line_of = (rows >= SPLIT).astype(int) * np.ones((1, X1 - X0), int)
cols = (np.arange(X1 - X0)[None, :] + X0) * np.ones((Y1 - Y0, 1), int)


BLK = 8
N_SWITCH = 569                                         # قبله: النص يُكتب فوق اليد (طبقة عليا)؛ بعده: تحت اليد
TMASK = cv2.dilate((np.abs(A_old) > 0.03).astype(np.uint8), np.ones((3, 3), np.uint8))
EDGES = list(range(X0, X1 + 1, BLK))
TMASK2 = cv2.dilate((np.abs(A_old) > 0.03).astype(np.uint8), np.ones((11, 11), np.uint8)) > 0


def clamp_halo(x, bg, m):
    """هالة الضغط الفاتحة حول النص القديم (تفتيح متساوٍ في القنوات فوق لون اللوح) تُردّ إلى لون اللوح."""
    d = x - bg
    neutral = (np.abs(d - d.mean(2, keepdims=True)).max(2) < 6) & (d.min(2) > 3)
    k = m & neutral
    x[k] = np.minimum(x[k], bg + 3)
    return x


class Patcher:
    """ظهور النص في الأصل ليس تلاشياً: يُكتب من اليمين لليسار، ويختفي ويعود؛ فتُقاس عتامته لكل سطر ولكل شريحة
    عرضها 8 بكسلات في كل إطار، ويُعطى النص الجديد العتامة نفسها في الموضع نفسه."""
    def __init__(self):
        self.prev = [np.zeros(X1 - X0, np.float32), np.zeros(X1 - X0, np.float32)]; self.log = []
        self.prevR = [np.zeros(X1 - X0, np.float32), np.zeros(X1 - X0, np.float32)]
        self.INKV = INKV

    def opac(self, r, bg):
        bgl = cv2.blur((np.abs(r - bg).max(2) < 20).astype(np.float32), (7, 7))
        ok = strong & (bgl > 0.45 * bgish_nb + 0.05)
        proj = ((r - bg) @ D_REF) / (D_REF @ D_REF) / np.maximum(A_old, 1e-3)
        O = np.zeros((Y1 - Y0, X1 - X0), np.float32); meas = []
        for l in (0, 1):
            xs, vs = [], []
            for a, b in zip(EDGES[:-1], EDGES[1:]):
                m = ok & (line_of == l) & (cols >= a) & (cols < b)
                if m.sum() >= 3: xs.append((a + b) / 2 - X0); v = float(np.clip(np.median(proj[m]), 0, 1.25)); vs.append(0.0 if v < 0.15 else v)
            if xs: o = np.interp(np.arange(X1 - X0), xs, vs).astype(np.float32); self.prev[l] = o
            else: o = self.prev[l]
            O[line_of[:, 0] == l] = o
            meas.append(len(xs))
        return O, meas

    def reveal(self, n, f):
        """طور الكتابة: النص طبقة عليا فوق اللوح واليد. يُستعاد ما تحته بالترميم، وتُقاس عتامته لكل شريحة، ثم يُرسم الجديد فوقه."""
        F = f.astype(np.float32)
        r = F[Y0:Y1, X0:X1]
        U = cv2.inpaint(np.ascontiguousarray(f[Y0:Y1, X0:X1]), TMASK, 3, cv2.INPAINT_TELEA).astype(np.float32)
        d = U - self.INKV
        O = np.zeros((Y1 - Y0, X1 - X0), np.float32); meas = []
        core = strong & (np.linalg.norm(d, axis=2) > 60)            # ما تحته ليس داكناً كالحبر (لا القلم)
        isink = np.abs(r - self.INKV).max(2) < 32
        ringm = (np.abs(A_old) < 0.05).astype(np.float32)
        ringink = cv2.blur((isink & (ringm > 0)).astype(np.float32), (9, 9)) / np.maximum(cv2.blur(ringm, (9, 9)), 1e-3)
        core &= ringink < 0.25                                       # ما حوله ليس داكناً (حافة القلم)
        pen = cv2.dilate((isink & (ringm > 0)).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        core &= ~pen
        for l in (0, 1):
            xs, vs = [], []
            for a, b in zip(EDGES[:-1], EDGES[1:]):
                m = core & (line_of == l) & (cols >= a) & (cols < b)
                if m.sum() >= 5:
                    v = float(isink[m].mean())
                    xs.append((a + b) / 2 - X0); vs.append(0.0 if v < 0.35 else (1.0 if v > 0.6 else v))
            if xs: o = np.interp(np.arange(X1 - X0), xs, vs).astype(np.float32); self.prevR[l] = o
            else: o = self.prevR[l]
            O[line_of[:, 0] == l] = o
            meas.append(len(xs))
        # ما تحت النص القديم: بالترميم حيث يظهر (أو قد يظهر)؛ وعلى اللوح لا يُسمح بأفتح من الخلفية (هالة الضغط)
        sel = (TMASK > 0) & ((O > 0) | (isink & ~pen))
        dev = np.abs(r - BG).max(2)
        fs = far & (dev < 20)
        bg = np.median(r[fs].reshape(-1, 3), 0) if fs.sum() > 200 else BG
        board = np.abs(U - bg).max(2) < 25
        Uc = np.where(board[..., None], np.minimum(U, bg + 2), U)
        uf = np.where(sel[..., None], Uc, r)
        uf = clamp_halo(uf, bg, TMASK2)
        an = (A_new * O)[..., None]
        out = f.copy()
        out[Y0:Y1, X0:X1] = np.clip(uf + (self.INKV - uf) * an + 0.5, 0, 255).astype(np.uint8)
        self.log.append((n, 'R', meas, round(float(O[strong].mean()), 3)))
        self.last = (np.zeros(O.shape, bool), O)
        return out

    def get(self, n, f):
        """بعد الكتابة: النص تحت اليد. فرق الحبر عن اللوح D_t يُقاس لكل قناة (يشمل التلاشي)، ويُعدَّل البكسل
        إذا لم يكن من اليد وكانت حوله خلفية لوح ظاهرة (فلا يُمسّ حبرٌ تحت القلم الداكن)."""
        if n < N_SWITCH: return self.reveal(n, f)
        F = f.astype(np.float32)
        r = F[Y0:Y1, X0:X1]
        dev = np.abs(r - BG).max(2)
        sel = far & (dev < 20)
        bg = np.median(r[sel].reshape(-1, 3), 0) if sel.sum() > 200 else BG.astype(np.float32)
        bgl = cv2.blur((np.abs(r - bg).max(2) < 20).astype(np.float32), (7, 7))
        ok = strong & (bgl > 0.45 * bgish_nb + 0.05)
        if not hasattr(self, 'D'): self.D = [D_REF.copy(), D_REF.copy()]
        Dimg = np.zeros(r.shape, np.float32)
        for l in (0, 1):                                              # لكل سطر (التلاشي غير متجانس بينهما)
            m = ok & (line_of == l)
            if m.sum() >= 25: self.D[l] = np.median((r[m] - bg) / A_old[m][:, None], 0).astype(np.float32)
            Dimg[line_of == l] = self.D[l]
        D = Dimg
        M = bg + A_old[..., None] * D
        q = (r + 1) / (M + 1)
        hand0 = (np.abs(r - M).max(2) > 28) & ((q.min(2) < 0.80) | (q.max(2) > 1.10) | (np.abs(q[..., 2] - q[..., 0]) > 0.07))
        nl, lab, st, _ = cv2.connectedComponentsWithStats(hand0.astype(np.uint8), 8)
        keep = np.zeros(nl, bool); keep[1:] = st[1:, 4] >= 10
        hand = cv2.dilate(keep[lab].astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        ringm = (np.abs(A_old) < 0.05).astype(np.float32)
        frac = cv2.blur(((~hand) & (ringm > 0)).astype(np.float32), (7, 7)) / np.maximum(cv2.blur(ringm, (7, 7)), 1e-3)
        w = ((~hand) & (ringm > 0)).astype(np.float32)
        gw = cv2.GaussianBlur(w, (0, 0), 3)
        Sh = np.where(gw > 0.05, cv2.GaussianBlur(q.mean(2) * w, (0, 0), 3) / np.maximum(gw, 1e-3), 1.0)
        consistent = np.abs(r - Sh[..., None] * M).max(2) < 22                # يطابق اللوح والنص القديم: مكشوف قطعاً
        edit = ((~hand) & (frac > 0.5)) | consistent
        delta = Sh[..., None] * (A_new - A_old)[..., None] * D
        delta[~edit] = 0
        res = r + delta
        zone = (TMASK2 | (A_new > 0.01)) & edit                       # اللوح مسطّح: يُعاد بناء منطقة النص كاملة
        synth = Sh[..., None] * (bg + A_new[..., None] * D)
        res[zone] = synth[zone]
        # بقايا الحبر القديم الظاهرة ملاصقة لحافة اليد (رمادية داكنة لا لون فيها): تُرمَّم مما حولها
        Lr = r.mean(2); chroma = r.max(2) - r.min(2)
        vd = (np.abs(A_old) > 0.3) & ~edit & (Lr < 0.75 * (Sh * bg.mean())) & (chroma < 40)
        if vd.any():
            mk = (cv2.dilate(vd.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & (TMASK > 0) & ~edit
            U = cv2.inpaint(np.clip(res + 0.5, 0, 255).astype(np.uint8), mk.astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32)
            res[mk] = U[mk]
        out = f.copy()
        out[Y0:Y1, X0:X1] = np.clip(res + 0.5, 0, 255).astype(np.uint8)
        self.log.append((n, [[round(float(v), 1) for v in d] for d in self.D], int(hand.sum()), int((~edit & ((np.abs(A_old) > 0.05) | (A_new > 0.05))).sum()), [round(v) for v in bg]))
        self.last = (~edit, None)
        return out


if __name__ == '__main__':
    # تشغيل تجريبي: n0..n1، ورقة مقارنة
    import subprocess
    n0, n1 = int(sys.argv[1]), int(sys.argv[2])
    W, H = 1920, 1080
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{n0 / 30:.4f}', '-i', f'{S}/splice/lesson04_new.mp4', '-frames:v', str(n1 - n0), '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    P = Patcher(); tiles = []
    for n in range(n0, n1):
        b = p.stdout.read(W * H * 3)
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        o = P.get(n, f)
        if (n - n0) % int(sys.argv[3]) == 0:
            c = np.hstack([f[400:560, 1360:1760], o[400:560, 1360:1760]]).copy()
            hm = np.zeros((160, 400), np.uint8); hm[Y0 - 400:Y1 - 400, X0 - 1360:X1 - 1360] = P.last[0] * 255
            c[:, :400][hm > 0] = (0.7 * c[:, :400][hm > 0] + 0.3 * np.array([255, 0, 255])).astype(np.uint8)
            cv2.putText(c, f'{n} {n / 30:.2f}', (5, 20), 0, 0.6, (0, 0, 255), 2); tiles.append(c)
    for l in P.log[::int(sys.argv[3])]: print(l)
    cv2.imwrite(f'{S}/txt/l4t_dbg.jpg', np.vstack(tiles))
