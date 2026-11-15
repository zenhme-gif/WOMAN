"""الدرس الثاني: نصوص الشرح الجديدة (ورقة التعديل) مركّبة من حروف صفحات المصدر نفسها (خط الشرح، 4K)."""
import sys, pickle, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt
from bt import P, assemble, scaled
from joint import joint

def cut(p, x0, xa=None, xb=None):
    a, b = p; a = a.copy()
    if xa is not None: a[:, :max(0, xa - x0)] = 0
    if xb is not None: a[:, max(0, xb - x0):] = 0
    return a, b

def W(n, base, xa, xb, ca=None, cb=None, pad=6, cxa=None, cxb=None, **kw):
    """كلمة/قطعة من سطر خط قاعدته base بين xa وxb؛ ca/cb: قصّ عند عمودين (يسار/يمين)."""
    x0, x1 = xa - pad, xb + pad
    p = P(n, x0, x1, int(base - 200), int(base + 110), base, cxa=(xa - 2 if cxa is None else cxa), cxb=(xb + 2 if cxb is None else cxb), **kw)
    return cut(p, x0, ca, cb)

def J(n, base, xa, xb):
    return joint(n, xa, xb, base)[0]


def Wc(n, base, xa, xb, ca=None, cb=None, small=700, **kw):
    """كقطعة W، لكن القص بالأعمدة للخط الرئيسي وحده؛ النقاط الصغيرة تُبقى كاملة إن وقع مركزها بين حدي القص."""
    x0 = xa - 6
    a, b = W(n, base, xa, xb, **kw)
    lo = (ca - x0) if ca is not None else -1e9; hi = (cb - x0) if cb is not None else 1e9
    nl, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.12).astype(np.uint8), 8)
    out = np.zeros_like(a)
    for j in range(1, nl):
        m = lab == j
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        if st[j, 4] < small:
            if lo <= cen[j][0] <= hi: out = np.maximum(out, np.where(m, a, 0))
        else:
            c = np.where(m, a, 0); c[:, :max(0, int(lo))] = 0
            if cb is not None: c[:, max(0, int(hi)):] = 0
            out = np.maximum(out, c)
    return out, b

G = 36                      # فراغ ما بين الكلمات
g = lambda *ps, gap=-2: assemble(list(ps), [gap] * (len(ps) - 1))   # حروف متصلة
line = lambda *ws: assemble(list(ws), [G] * (len(ws) - 1))

# ===== الشريحة الثالثة للنفاس: «فليس نفاسًا، بل هو دم فساد، حكمه حكم الاستحاضة إلا أن يصادف عادتها في الحيض فيكون حيضًا»
fa_ini = W(90, 1715, 2950, 3135, ca=J(90, 1715, 3040, 3090))          # فـ (من «فهي»)
lays = W(80, 1547, 2998, 3216)                                          # ليس
falays = g(fa_ini, lays, gap=-6)
nifasan = W(80, 1547, 2680, 2963)                                       # نفاسًا،
bal = W(80, 1547, 2541, 2647)                                           # بل
huwa = W(73, 1884, 1690, 1880, ca=None, cb=J(73, 1884, 1800, 1840))     # هو (من «وهو»)
dam_fasad = W(80, 1547, 2103, 2506, down=0.35)                          # دم فساد،
hukmuh = W(80, 1547, 1742, 2066, cb=J(80, 1547, 2000, 2040))            # حكمه (من «وحكمه»)
rest1 = W(80, 1547, 778, 1712)                                          # حكم الاستحاضة إلا
an = W(48, 1547, 2510, 2635)                                            # أن
ya_ini = W(60, 1547, 1808, 2030, ca=1955)                               # يـ (من «يحرم»)
sad = W(115, 1547, 1897, 2137, cb=J(115, 1547, 2080, 2115))            # ـصاد (من «الصادق»)
fa_iso = W(114, 1715, 1690, 1800)                                       # ف (من «ويضاف»)
yusadif = g(ya_ini, sad, fa_iso, gap=-3)
rest2 = W(80, 1715, 1091, 2501)                                         # عادتها في الحيض فيكون حيضًا


# ===== قطع مشتركة
yahrum = W(60, 1547, 1808, 2030)                                        # يحرم
alayhima = W(92, 1547, 2574, 2847)                                      # عليهما
masjid = W(58, 1719, 1765, 2130)                                        # المسجد
wa = W(73, 1884, 1815, 1880, cxa=1818)                                  # و (من «وهو»)
comma = W(78, 1547, 2841, 2863)                                         # ،
fi = W(80, 1715, 2113, 2198)                                            # في
fih = W(82, 1547, 2581, 2728)                                           # فيه
semi = W(48, 1547, 1400, 1445, cxb=1445)                                # ؛
# دخول
dukhul = W(69, 1715, 1577, 1839)
# واللبث: و + الل (من «اللجنة») + بـ (من «به») + ـث (من «لحديث»)
all_ = W(73, 1884, 1050, 1140, ca=1050)
ba_ini = W(73, 1884, 1180, 1270, ca=1236)
tha_fin = W(78, 1547, 1079, 1224, cb=1160)
wallubth = g(all_, ba_ini, tha_fin, gap=-3)
wallubth = assemble([wa, wallubth], [10])
# المرور ، إن ، خافتا ، تلويثه
murur = W(61, 1547, 1859, 2125)
in_ = W(74, 1884, 1178, 1290, cxb=1290)
kha = W(57, 1715, 2996, 3099)                                           # خا
fa_i2 = W(73, 1884, 1310, 1543, ca=1458, cxb=1520)                      # فـ (من «أفتت»)
ta_a = W(84, 1547, 2712, 2902, cb=2783)                                 # ـتا (من «يحتاج»)
khafata = assemble([kha, g(fa_i2, ta_a, gap=-3)], [8])
til = W(88, 1883, 1698, 1887, ca=1812)                                  # تلـ
waw_f = W(79, 1547, 3007, 3159, cb=3065, cxa=3005)                      # ـو (من «تعود»)
tha_m = W(73, 1547, 1250, 1367, ca=1277, cb=1318)                       # ـثـ (من «الثاني»)
ha_f = W(82, 1547, 2581, 2728, cb=2632)                                 # ـه (من «فيه»)
talwithih = assemble([g(til, waw_f, gap=-3), g(ya_ini, tha_m, ha_f, gap=-3)], [6])
fainna = W(53, 1715, 3054, 3220)
amanat_ = W(124, 1547, 1218, 1447, ca=1300, cxb=1446, extra=lambda cx, cy, st: 1380 <= cy <= 1605 and not (cy < 1432 and cx > 1420))   # أمنـ (بلا ضمة)                  # أمنـ
amanata = g(amanat_, ta_a, gap=-3)
rest_g9 = W(61, 1547, 1322, 2524)                                       # لم يحرم المرور عند الحاجة
hadith_g9 = W(58, 1719, 900, 2945)                                      # لقوله ﷺ : (لا أُحِلّ المسجد لحائض ولا جنب)
# ===== النفاس ١
laqul = W(66, 1715, 2960, 3190)
umm_salama = W(78, 1547, 671, 1038, extra=lambda cx, cy, st: 1426 <= cy <= 1568)
l2a = W(78, 1715, 1511, 3206, down=0.75)                                           # رضي الله عنها : (كانت النفساء تجلس
l2b = W(78, 1715, 634, 1478, down=0.75)                                            # على عهد رسول الله
l3 = W(78, 1888, 1600, 2245)                                            # ﷺ أربعين يومًا)
# ===== النفاس ٢
alif = W(79, 1547, 1450, 1465, cxa=1450)                                # ا
gh_i = W(69, 1883, 2160, 2400, ca=J(69, 1883, 2320, 2350))              # غـ (أول، من «غسل»)
tas = Wc(78, 1547, 2873, 3175, ca=2943, cb=3082)       # ـتسـ (من «تغتسل»)
lat = W(95, 1715, 607, 968, cb=745)                                     # ـلت
ightasalat = assemble([alif, g(gh_i, tas, lat, gap=-3)], [10])
salat = W(122, 1547, 1075, 1334)                                        # صلت
sa = W(115, 1547, 1961, 2137, cb=2098, cxa=1958)                        # ـصا
mim_i = W(73, 1884, 1589, 1667, ca=1618)                                # مـ
ta_f = W(78, 1715, 2226, 2361, cb=2300)                                 # ـت
samat = assemble([sa, g(mim_i, ta_f, gap=-3)], [10])
ha_i = W(79, 1547, 1813, 2004, ca=1938)                                 # حـ
halat = g(ha_i, lat, gap=-3)
w = lambda x: assemble([wa, x], [10])
zawjiha = W(78, 1547, 1456, 1745)
aad = W(80, 1715, 2354, 2501)                                           # عاد
hamza_alif = W(80, 1547, 845, 875, cxa=845, down=0.9)                             # إ
layha = W(50, 1547, 1856, 2065, cb=1999)                                # ـليها
ilayha = assemble([hamza_alif, layha], [8])
aldam = W(79, 1547, 1288, 1462)
qabl = W(6, 1547, 1960, 2117)
ta_i = W(78, 1715, 1511, 1826, ca=1772)                                 # تـ
mim_m = W(78, 1547, 671, 919, ca=738, cb=806)                           # ـمـ
alif_f = W(73, 1884, 1589, 1667, cb=1618)                               # ـا
mim_iso = W(78, 1547, 954, 1008)                                        # م
tamam = assemble([g(ta_i, mim_m, alif_f, gap=-3), mim_iso], [6])
al_a = W(73, 1547, 2665, 2760, up=1.7)                                          # الأ
rbain = W(79, 1547, 683, 926, cxb=932)                                  # ربعين
alarbain = assemble([al_a, rbain], [4])
fahi = W(90, 1715, 2950, 3135)
nufasa = W(79, 1547, 2650, 2921, cxa=2648)                              # نفساء
hatta_aw = W(79, 1547, 1169, 2004)                                      # حتى ينقطع الدم أو
tim = W(79, 1547, 996, 1144, cb=1106)                                   # ـتم
yatim = g(ya_ini, tim, gap=-3)
laha = W(48, 1715, 1769, 1874)
arba = W(79, 1547, 683, 959, ca=805, up=1.7)                                    # أربعـ
wn = W(80, 1715, 1394, 1683, cb=1530)                                   # ـون
arbaun = g(arba, wn, gap=-3)
yawman = W(79, 1715, 1838, 2008)

if __name__ == '__main__':
    N3a = line(falays, nifasan, bal, huwa, dam_fasad, hukmuh, rest1)
    N3b = line(an, yusadif, rest2)
    G9a = line(yahrum, alayhima, dukhul, masjid, wallubth, assemble([fih, semi], [6]))
    G9b1 = line(yahrum, alayhima, murur, fi, masjid, in_, khafata, assemble([talwithih, comma], [6]))
    G9b2 = line(fainna, amanata, talwithih, rest_g9)
    N1a = line(laqul, umm_salama, l2a)
    N1b = line(l2b, l3)
    N2a = line(ightasalat, w(salat), w(samat), w(halat), assemble([zawjiha, comma], [6]), fainna, aad, ilayha)
    N2b = line(aldam, qabl, tamam, alarbain, fahi, nufasa, hatta_aw)
    N2c = line(yatim, laha, arbaun, yawman)
    pickle.dump(dict(N3a=N3a, N3b=N3b, G9a=G9a, G9b1=G9b1, G9b2=G9b2, N1a=N1a, N1b=N1b, N2a=N2a, N2b=N2b, N2c=N2c, hadith_g9=hadith_g9), open(f'{bt.S}/txt/l2body.pkl', 'wb'))
    bt.preview([G9a, hadith_g9, G9b1, G9b2], f'{bt.S}/txt/l2_g9.png', sc=0.5)
    bt.preview([N1a, N1b, N2a, N2b, N2c], f'{bt.S}/txt/l2_n12.png', sc=0.5)
    for k, v in dict(G9a=G9a, G9b1=G9b1, G9b2=G9b2, N1a=N1a, N1b=N1b, N2a=N2a, N2b=N2b, N2c=N2c).items(): print(k, v[0].shape[1])
    bt.preview([N3a, N3b], f'{bt.S}/txt/l2_n3.png', sc=0.5)
    bt.preview([fa_ini, falays, huwa, hukmuh, an, ya_ini, sad, fa_iso, yusadif], f'{bt.S}/txt/l2_n3p.png', sc=0.6)
    print('w', N3a[0].shape, N3b[0].shape)
