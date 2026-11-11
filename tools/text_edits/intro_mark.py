"""الدرس الأول، المقدمة: حرف أحمر من زخرفة اسم الشيخ يظهر عند 0:14.6 قبل أن يبلغه القلم (0:18.2).
يُمحى إلى أن يمر القلم عليه، ثم يظهر من اليمين إلى اليسار مع مروره (18.23–18.33)."""
import sys, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/regroup')
import partial as PT
V = '/home/user/WOMAN/lessons/lesson01-taharah-wudu-ghusl.mp4'
Y0, Y1, X0, X1 = 810, 948, 604, 660
T0, R0, R1 = 14.6, 18.23, 18.33


class IntroMark:
    def __init__(self):
        mk = PT.frame(V, 16.5)[Y0:Y1, X0:X1].astype(int)
        self.mk = mk
        red = (mk[..., 2] - mk[..., 1] > 12) & (mk[..., 2] - mk[..., 0] > 12)
        self.M = cv2.dilate(red.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        self.bg = PT.frame(V, 14.0)[Y0:Y1, X0:X1]
        self.n0, self.n1 = int(round(T0 * 30)), int(round(R1 * 30))

    def get(self, n, f):
        t = n / 30
        g = f.copy(); r = g[Y0:Y1, X0:X1]
        same = np.abs(r.astype(int) - self.mk).max(2) < 40          # الحرف ظاهر هنا (لا يد فوقه)
        m = self.M & same
        if t >= R0:
            front = X1 - (t - R0) / (R1 - R0) * (X1 - X0)          # ما يمين رأس القلم قد كُتب
            m &= (np.arange(X0, X1)[None, :] < front)
        r[m] = self.bg[m]
        return g
