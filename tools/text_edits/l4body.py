"""الدرس الرابع: نص الشرح في ص131 (حذف الحديث) وص135 (السطر الأول)."""
import sys, pickle, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt
from bt import P, assemble

def cut(p, x0, xa=None, xb=None):
    a, b = p; a = a.copy()
    if xa is not None: a[:, :max(0, xa - x0)] = 0
    if xb is not None: a[:, max(0, xb - x0):] = 0
    return a, b

G = 36
# ص131 السطر الثاني: «النساء قبل الرجال»
p131_l2 = P(131, 2420, 3230, 1570, 1800, 1715, extra=lambda cx, cy, st: 1598 <= cy <= 1759 and not (2790 <= cx <= 2845 and cy < 1630))   # بلا نقطتي ياء «النبي» من السطر الأول
# ص135 السطر الأول: «إمامة النساء تكون وسطهن لفعل عائشة رضي الله عنها،»
alif_h = P(135, 3108, 3140, 1420, 1620, 1547, cxa=3110)                            # إ
ma = P(133, 1975, 2066, 1930, 2120, 2052, cxa=1980, cxb=2064)                      # ما
mah = cut(P(131, 1790, 1930, 1590, 1790, 1715, cxb=1925, down=0.45), 1790, xb=1910)  # مة (من «سلمة»)
imama = assemble([alif_h, ma, mah], [10, 12])
nisa = P(135, 1912, 2196, 1420, 1620, 1547, cxa=1915)                              # النساء
takun = P(135, 2510, 2760, 1420, 1620, 1547)                                       # تكون
wasat = P(135, 2225, 2490, 1420, 1620, 1547, cxa=2228)                             # وسط
hun = cut(P(131, 2135, 2290, 1760, 1960, 1887, cxb=2284), 2135, xb=2281)           # ـهن (من «بيوتهن»)
wasathun = assemble([wasat, hun], [-3])
lifil = P(135, 920, 1900, 1420, 1620, 1547, cxa=922, cxb=1898)                     # لفعل عائشة رضي الله
anha = P(131, 1150, 1340, 1590, 1790, 1715, cxa=1152, cxb=1335, down=0.45)          # عنها
comma = P(135, 695, 730, 1420, 1620, 1547, cxb=728)                                 # ،
p135_l1 = assemble([imama, nisa, takun, wasathun, lifil, assemble([anha, comma], [6])], [G] * 5)
if __name__ == '__main__':
    pickle.dump(dict(p131_l2=p131_l2, p135_l1=p135_l1), open(f'{bt.S}/txt/l4body.pkl', 'wb'))
    bt.preview([p131_l2, p135_l1, imama, wasathun], f'{bt.S}/txt/l4body.png', sc=0.5)
    print(p131_l2[0].shape, p135_l1[0].shape)
