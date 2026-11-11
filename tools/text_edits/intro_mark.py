"""الدرس الأول، المقدمة: حرف أحمر من زخرفة اسم الشيخ يظهر عند 0:14.6 قبل أن يبلغه القلم (0:18.2).
يُمحى إلى أن يمر القلم عليه، ثم يظهر من اليمين إلى اليسار مع مروره (18.23–18.33)."""
import sys, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/regroup')
import partial as PT
V = '/home/user/WOMAN/lessons/lesson01-taharah-wudu-ghusl.mp4'
Y0, Y1, X0, X1 = 810, 948, 604, 660
T0, R0, R1 = 14.6, 18.23, 18.33


class IntroMark:
    """v: الفيديو؛ t0: ظهور الحرف مبكراً؛ r0–r1: مرور القلم عليه (يظهر فيه من اليمين إلى اليسار)."""
    def __init__(self, v=V, t0=T0, r0=R0, r1=R1):
        self.R0, self.R1 = r0, r1
        mk = PT.frame(v, t0 + 1.9)[Y0:Y1, X0:X1].astype(int)
        self.mk = mk
        red = (mk[..., 2] - mk[..., 1] > 12) & (mk[..., 2] - mk[..., 0] > 12)
        self.M = cv2.dilate(red.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        self.bg = PT.frame(v, t0 - 0.6)[Y0:Y1, X0:X1]
        self.n0, self.n1 = int(round((t0 - 0.05) * 30)), int(round(r1 * 30))

    def get(self, n, f):
        t = n / 30
        g = f.copy(); r = g[Y0:Y1, X0:X1]
        same = np.abs(r.astype(int) - self.mk).max(2) < 40          # الحرف ظاهر هنا (لا يد فوقه)
        m = self.M & same
        if t >= self.R0:
            front = X1 - (t - self.R0) / (self.R1 - self.R0) * (X1 - X0)          # ما يمين رأس القلم قد كُتب
            m &= (np.arange(X0, X1)[None, :] < front)
        r[m] = self.bg[m]
        return g


# الدروس الأربعة: المقدمة نفسها بإزاحات زمنية (ظهور الحرف، ومرور القلم قبل أول حبر أزرق يساره بـ0.17–0.07 ث)
LESSONS = {1: (14.6, 18.23, 18.33), 2: (10.4, 12.86, 12.96), 3: (14.6, 18.23, 18.33), 4: (8.27, 10.20, 10.30)}
