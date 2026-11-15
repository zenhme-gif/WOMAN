"""الدرس الثاني: نصوص اللافتة والمربعات الجديدة بخط العناوين، من حروف اللافتات والمربعات الأصلية."""
import sys, pickle, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt, tf
from tf import T
from bt import assemble

def cut(p, x0, xa=None, xb=None):
    a, b = p; a = a.copy()
    if xa is not None: a[:, :max(0, xa - x0)] = 0
    if xb is not None: a[:, max(0, xb - x0):] = 0
    return a, b

GW = 40
BAN1, BAN2, BOX = (380, 600, 532), (520, 780, 709), (1000, 1300, 1182)
t = lambda n, x0, x1, yb, **kw: T(n, x0 - 5, x1 + 5, yb[0], yb[1], yb[2], cxa=x0 - 3, cxb=x1 + 3, **kw)
# اللافتة
nifas = t(77, 1546, 1907, BAN1, down=0.12)                                  # النفاس
akthar_mudda = t(77, 1955, 2352, BAN1, down=0.12)                           # أكثر مدة
arbaun_yawma = t(77, 1644, 2195, BAN2, up=1.42)                           # أربعون يوما
# المربعات
idha_raat = t(78, 1890, 2240, BOX)                               # إذا رأت
idha = t(78, 2127, 2240, BOX)                                    # إذا
tuhr = t(78, 1566, 1844, BOX)                                    # الطهر
qabl_tamam = t(77, 2058, 2481, BOX)                              # قبل تمام
arbain = t(77, 1355, 1736, BOX)                                  # الأربعين
bad = t(80, 2188, 2351, BOX)                                     # بعد
BAN81 = (460, 740, 620)
nufasa = T(44, 1312, 1700, 460, 740, 620, cxa=1314, cxb=1697, down=0.08)                # النفساء (بلا الواو)
min_marah = t(81, 1614, 2078, BAN81)                             # من المرأة
dam = cut(t(81, 2421, 2620, BAN81), 2416, xb=2552)               # دم (من «الدم»)
nun_i = cut(t(81, 2265, 2325, BAN81), 2260, xa=2268, xb=2314)    # نـ (من «النازل»)
zal = t(81, 2113, 2232, BAN81)                                   # زل
nazal = assemble([nun_i, zal], [-4])
BANNER = nifas
BOX_N1 = [assemble([akthar_mudda, nifas], [GW]), arbaun_yawma]
BOX_N2 = [assemble([idha_raat, nufasa, tuhr], [GW, GW]), assemble([qabl_tamam, arbain], [GW])]
BOX_N3 = [assemble([idha, nazal, min_marah, dam], [GW, GW, GW]), assemble([bad, arbain], [GW])]
if __name__ == '__main__':
    pickle.dump(dict(BANNER=BANNER, BOX_N1=BOX_N1, BOX_N2=BOX_N2, BOX_N3=BOX_N3), open(f'{bt.S}/txt/l2title.pkl', 'wb'))
    bt.preview([BANNER] + BOX_N1 + BOX_N2 + BOX_N3, f'{bt.S}/txt/l2title.png', sc=0.5)
    bt.preview([nufasa, dam, nun_i, zal, nazal], f'{bt.S}/txt/l2tpieces.png', sc=0.7)
    for k, v in [('ban', BANNER)] + [(f'n1_{i}', x) for i, x in enumerate(BOX_N1)] + [(f'n2_{i}', x) for i, x in enumerate(BOX_N2)] + [(f'n3_{i}', x) for i, x in enumerate(BOX_N3)]: print(k, v[0].shape)
