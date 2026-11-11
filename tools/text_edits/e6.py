"""الدرس الثالث، ص116: «كنوم من غير فعل أسباب الاستيقاظ، أو لأن الوضوء يذهب المكياج، / فلا يجوز فقد توعَّد الله ... فقال سبحانه :»"""
import sys, pickle, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt
from bt import P, assemble, scaled

def cut(p, x0, xa=None, xb=None):
    """يقص القطعة عند حدود أفقية بإحداثيات الصفحة (x0 = بداية القطعة)."""
    a, b = p; a = a.copy()
    if xa is not None: a[:, :max(0, xa - x0)] = 0
    if xb is not None: a[:, max(0, xb - x0):] = 0
    return a, b

def boost(p):
    a, b = p; return np.clip(a / max(a.max(), 1e-3), 0, 1).astype(np.float32), b

G = 36
konom = P(116, 2225, 2980, 1400, 1640, 1547)                                       # كنوم من غير فعل
alif = P(116, 1688, 1720, 1400, 1640, 1547, cxa=1690)                              # أ (من «أو»)
sabab = P(116, 1745, 2062, 1400, 1640, 1547, cxb=2060)                             # سباب،  (من «الأسباب،»)
asbab = assemble([alif, cut(sabab, 1745, xa=1778)], [10])                          # أسباب (بلا فاصلة)
comma = cut(sabab, 1745, xb=1778)                                                  # ،
# الاستيقاظ
als = cut(P(48, 1500, 1730, 1580, 1780, 1715, cxa=1530), 1500, xa=1536)            # الاسـ
tay = scaled(boost(cut(P(62, 2380, 2500, 1000, 1260, 1181, ah=111, cxa=2396), 2380, xa=2398)), 98 / 111)  # تيـ
qat = cut(P(86, 2500, 2760, 1380, 1640, 1547, cxb=2712), 2500, xb=2708)            # ـقاط
dot = (bt.alpha(bt.page(69)[1795:1822, 1507:1534]), 1883 - 1795)                  # نقطة الظاء
# نقطة الظاء فوق «ـقاط»: مركزها يمين الساق بـ45.5 وفوق خط القاعدة بـ75.5 (كما في «والتحفظ»)
qa, qb = qat; qa = qa.copy()
cx, cy = 2533 + 45.5 - 2500, qb - 75.5
d = dot[0]; y0 = int(round(cy - d.shape[0] / 2)); x0 = int(round(cx - d.shape[1] / 2))
qa[y0:y0 + d.shape[0], x0:x0 + d.shape[1]] = np.maximum(qa[y0:y0 + d.shape[0], x0:x0 + d.shape[1]], d)
qaz = (qa, qb)
istiqadh = assemble([als, tay, qaz], [-3, -4])
aw = P(116, 1625, 1720, 1400, 1640, 1547)                                          # أو
lian = P(24, 3020, 3195, 1560, 1780, 1715, cxa=3025)                               # لأن
wudu = P(23, 1525, 1880, 1420, 1620, 1547, cxa=1530, cxb=1872, down=0.35)          # الوضوء
ya = cut(P(116, 1055, 1112, 1400, 1640, 1547, cxa=1058), 1055, xa=1063)            # يـ
dhal = cut(P(116, 2440, 2505, 1600, 1800, 1715, cxb=2504), 2440, xb=2500)          # ـذ
ha = cut(P(26, 2535, 2615, 1580, 1800, 1715, cxa=2536), 2535, xa=2543)             # هـ
ba = scaled(cut(P(33, 1025, 1135, 1580, 1760, 1674, ah=84, cxb=1132), 1025, xb=1128), 98 / 84)   # ـب
yadhhab = assemble([ya, dhal, ha, ba], [-3, 6, -3])
mak = cut(P(113, 1545, 1760, 1400, 1640, 1547, cxa=1548), 1545, xa=1554)          # المكـ
yaj = cut(P(116, 1100, 1490, 1400, 1640, 1547, cxa=1290), 1100, xb=1483)           # ـياج،
makiyaj = assemble([mak, yaj], [-4])
fala = P(116, 860, 1262, 1400, 1640, 1547, cxa=862, cxb=1262)                      # فلا يجوز
line2 = P(116, 600, 3300, 1590, 1800, 1715, down=0.45)                                        # فقد توعّد ... فقال سبحانه :
L1 = assemble([konom, asbab, assemble([istiqadh, comma], [6]), aw, lian, wudu, yadhhab, makiyaj], [G] * 7)
L2 = assemble([fala, line2], [G])
if __name__ == '__main__':
    pickle.dump(dict(L1=L1, L2=L2), open(f'{bt.S}/txt/e6.pkl', 'wb'))
    bt.preview([L1, L2], f'{bt.S}/txt/e6_lines.png', sc=0.5)
    bt.preview([asbab, istiqadh, yadhhab, makiyaj, als, tay, qaz, ya, dhal, ha, ba, mak, yaj], f'{bt.S}/txt/e6_pieces.png', sc=0.8)
    print('widths', L1[0].shape, L2[0].shape)
