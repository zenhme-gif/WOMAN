"""الدرس الرابع: نصوص اللافتة والمربعات بخط العناوين، من حروف اللافتات والمربعات الأصلية."""
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

GW = 40                                                                             # بين الكلمات
alif_h = T(17, 2480, 2545, 1040, 1240, 1208, cxa=2485)                             # أ (من «أن»)
dhan = T(122, 2150, 2335, 470, 700, 619, cxa=2155, cxb=2332)                       # ذان (من «الأذان»)
dha = T(122, 2245, 2335, 470, 700, 619, cxa=2248, cxb=2332)                        # ذا
nun_i = cut(T(113, 2160, 2210, 470, 700, 619, cxa=2165), 2160, xa=2170)            # نـ (من «نصف»)
ha = cut(T(116, 1365, 1460, 470, 700, 619, cxb=1455), 1365, xb=1450)               # ـها (من «وقتها»)
taha = cut(T(116, 1365, 1505, 470, 700, 619, cxb=1500), 1365, xb=1501)             # ـتها
haa_m = cut(T(116, 1390, 1460, 470, 700, 619, cxa=1395, cxb=1455), 1390, xa=1397, xb=1450)  # ـهـ
waw = T(122, 2075, 2130, 470, 700, 619, cxa=2078)                                  # و (من «والإقامة»)
hamza_i = T(133, 2430, 2470, 470, 720, 619, cxa=2432)                              # إ (من «إمامة»)
qa = T(122, 1862, 1952, 470, 700, 619, cxa=1866, cxb=1950)                         # قا
mim_i = cut(T(90, 2555, 2630, 470, 700, 619, cxa=2560), 2555, xa=2562)             # مـ (من «من»)
marah = T(133, 1875, 2160, 470, 700, 619, cxa=1878, cxb=2158)                      # المرأة
lirijal = T(129, 1520, 1865, 470, 700, 619, cxa=1525, cxb=1862)                    # للرجال
rijal = cut(T(129, 1520, 1865, 470, 700, 619, cxa=1525, cxb=1862), 1520, xb=1809)  # لرجال (بلا اللام الأولى)
alif = T(122, 2435, 2465, 470, 700, 619, cxa=2438)                                 # ا (من «الأذان»)
linnisa = T(122, 1365, 1695, 470, 700, 619, cxa=1368)                              # للنساء
nun_m = cut(T(122, 1570, 1622, 470, 700, 619, cxa=1576, cxb=1617), 1570, xa=1574, xb=1617)   # ـنـ
bayn = T(84, 2185, 2370, 1000, 1180, 1122, cxa=2205)                               # بين
bay = cut(bayn, 2185, xa=2245)                                                     # بيـ (بلا النون)
nun_f = cut(bayn, 2185, xb=2250)                                                   # ـن
bila_satir = T(136, 1700, 2110, 1040, 1240, 1181)                                  # بلا ساتر
maa_wujud_satir = T(137, 1550, 2270, 1080, 1250, 1180)                             # مع وجود ساتر

adhan = assemble([alif_h, dhan], [10])
adhanha = assemble([alif_h, dha, assemble([nun_i, ha], [-3])], [10, 12])
iqamatiha = assemble([waw, hamza_i, qa, assemble([mim_i, taha], [-3])], [10, 10, 12])
al_rijal = assemble([alif, rijal], [8])
baynahunna = assemble([bay, nun_m, haa_m, nun_f], [-3, -3, -3])
wabayn = assemble([waw, bayn], [10])
TITLE = assemble([adhan, marah, iqamatiha], [GW, GW])
BOX_ILLA = assemble([adhanha, iqamatiha, lirijal], [GW, GW])
BOX_HUKM = assemble([adhanha, iqamatiha, linnisa], [GW, GW])
BOX136 = [assemble([bila_satir, baynahunna], [GW]), assemble([wabayn, al_rijal], [GW])]
BOX137 = [maa_wujud_satir, assemble([baynahunna, wabayn, al_rijal], [GW, GW])]
if __name__ == '__main__':
    pickle.dump(dict(TITLE=TITLE, BOX_ILLA=BOX_ILLA, BOX_HUKM=BOX_HUKM, BOX136=BOX136, BOX137=BOX137), open(f'{bt.S}/txt/l4title.pkl', 'wb'))
    bt.preview([TITLE, BOX_ILLA, BOX_HUKM] + BOX136 + BOX137, f'{bt.S}/txt/l4title.png', sc=0.5)
    bt.preview([adhanha, iqamatiha, baynahunna, al_rijal, wabayn, nun_i, ha, mim_i, taha, bay, nun_m, haa_m, nun_f], f'{bt.S}/txt/l4tpieces.png', sc=0.6)
    for k, v in [('TITLE', TITLE), ('ILLA', BOX_ILLA), ('HUKM', BOX_HUKM), ('136a', BOX136[0]), ('136b', BOX136[1]), ('137a', BOX137[0]), ('137b', BOX137[1])]: print(k, v[0].shape)
