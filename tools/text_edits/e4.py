"""القول الثاني في خريطة التنجية (الدرس الأول) بالنص المطلوب، من قطع الصفحات بمقياسها الأصلي (ألف ≈ 98)."""
import sys, pickle, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt
from bt import P, assemble, scaled, trim

def cut(p, xa=None, xb=None):
    """يقص قطعة (ألفا، خط قاعدة) بحدود أفقية بإحداثيات القطعة."""
    a, b = p; a = a.copy()
    if xa is not None: a[:, :xa] = 0
    if xb is not None: a[:, xb:] = 0
    return a, b

G = 36                                                   # المسافة بين الكلمات (من الصفحة 23)
# السطر الأول
la_yanqud = P(23, 1530, 2320, 1420, 1620, 1547, down=0.35)                                   # لا ينقض الوضوء
lian = P(24, 3020, 3195, 1560, 1780, 1715, cxa=3025)                               # لأن
raj = cut(P(82, 1660, 1800, 1420, 1620, 1547), xa=1668 - 1660)                     # رجـ
lla = cut(P(72, 1200, 1350, 1420, 1580, 1547), xb=1288 - 1200)                     # ـلا
rajula = assemble([raj, lla], [-4])
sa = P(31, 1450, 1720, 1560, 1780, 1719, cxa=1594)                                 # سأ
lam = P(23, 1870, 1925, 1600, 1760, 1715, cxb=1920)                                # ل
saala = assemble([sa, lam], [10])
nabi = P(131, 2685, 3220, 1380, 1660, 1551, cxa=2688, cxb=3035)                             # النبي ﷺ
alif = P(29, 2760, 2800, 1600, 1760, 1719, cxa=2765)                               # أ
yatawadda = P(29, 1680, 1980, 1740, 1940, 1882)                                    # يتوضأ
aytawadda = assemble([alif, yatawadda], [12])
# السطر الثاني
ahad = P(124, 2200, 2560, 1760, 1950, 1884, cxa=2340)                              # أحد
na = cut(P(91, 1815, 1900, 1580, 1780, 1719), xb=1880 - 1815)                      # نا
ahadna = assemble([ahad, na], [10])
idha = P(131, 2540, 2665, 1400, 1640, 1551)                                        # إذا
mas_dhakarah = P(23, 2100, 2560, 1600, 1780, 1715, cxa=2112)                                 # مس ذكره
q = P(50, 980, 1050, 1580, 1790, 1719, cxa=985, cxb=1045)                        # ؟
faqala = P(23, 1795, 2090, 1600, 1780, 1715, cxa=1798)                                       # فقال :
hadith = P(23, 830, 1770, 1560, 1800, 1715, cxa=835)                               # (إِنَّمَا هُوَ بَضْعَةٌ مِنْك
paren = P(23, 1718, 1768, 1760, 1900, 1883, cxb=1745)                              # )
# السطر الثالث
wahuwa = P(23, 1430, 2400, 1930, 2150, 2052)                                       # وهو اختيار ابن تيمية

# نقطة آخر الجملة: من «المقدّم.» (الصفحة 10، خطها أصغر: ألف 76)
dot = scaled(P(10, 1355, 1382, 1490, 1530, 1521, cxb=1375), 98 / 76)
# فتحة الكاف في «مِنْكَ»: فتحة «هُوَ بَضْعَةٌ» (x 1407، y 1641) تُنسخ فوق الكاف
ha, hb = hadith; ha = ha.copy()
fat = bt.alpha(bt.page(23)[1638:1658, 1404:1444])
fy, fx = 1620 - 1560, 889 - 830
ha[fy:fy + fat.shape[0], fx:fx + fat.shape[1]] = np.maximum(ha[fy:fy + fat.shape[0], fx:fx + fat.shape[1]], fat)
hadith = (ha, hb)
L1 = assemble([la_yanqud, lian, rajula, saala, nabi, aytawadda], [G] * 5)
L2 = assemble([ahadna, idha, assemble([mas_dhakarah, q], [8]), faqala, assemble([hadith, paren], [4])], [G] * 4)
L3 = assemble([wahuwa, dot], [8])
if __name__ == '__main__':
    pickle.dump(dict(L1=L1, L2=L2, L3=L3), open(f'{bt.S}/txt/e4.pkl', 'wb'))
    bt.preview([L1, L2, L3], f'{bt.S}/txt/e4_lines.png', sc=0.6)
