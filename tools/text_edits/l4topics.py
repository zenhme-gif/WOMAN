"""الدرس الرابع، شريحة «موضوعات الدرس»: نص المربع الأول «حكم الأذان / والإقامة للنساء» ← «أذان المرأة / وإقامتها»
بخط تجوّل (Tajawal) بالمقاس 54 (4K) نفسه، متوسطاً على مركزي السطرين القديمين وعلى خطي قاعدتيهما."""
import sys, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/hr')
from PIL import Image, ImageDraw, ImageFont
import build_topics as T
S = T.S
OLD = ['حكم الأذان', 'والإقامة للنساء']
NEW = ['أذان المرأة', 'وإقامتها']
SIZE = 54


def rb(text, size=SIZE):
    """ألفا 4K مقصوصة على الحبر + بعد خط القاعدة عن أعلى القص + عرض الحبر."""
    f = ImageFont.truetype(T.FONT, size)
    im = Image.new('L', (1600, 400), 0)
    ImageDraw.Draw(im).text((1500, 250), text, font=f, fill=255, anchor='rs', direction='rtl', language='ar')
    a = np.asarray(im).astype(np.float32) / 255
    ys, xs = np.nonzero(a > 0.02)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 250 - ys.min()


def layers():
    s1 = cv2.imread(f'{S}/slides/out_orig/درس4/01.png')
    g = cv2.cvtColor(s1, cv2.COLOR_BGR2GRAY).astype(np.float32)
    # مواضع السطرين القديمين بالمطابقة (كما بُنيت شريحة 4K)
    boxes = [(1495, 449, 1614, 477), (1462, 486, 1644, 511)]
    A4 = np.zeros((2160, 3840), np.float32)
    info = []
    for (bx, old, new) in zip(boxes, OLD, NEW):
        sc, t, size, x, y = T.fit_line(g, bx, [old], 73.0)
        assert t == old and size == SIZE, (t, size)
        ao, bo = rb(old)
        a0 = T.render4(old, size)
        assert a0.shape == ao.shape, (a0.shape, ao.shape)
        X, Y = 2 * x, 2 * y                      # أعلى يسار القديم في 4K
        base = Y + bo; cx = X + ao.shape[1] / 2
        an, bn = rb(new)
        X1 = int(round(cx - an.shape[1] / 2)); Y1 = base - bn
        A4[Y1:Y1 + an.shape[0], X1:X1 + an.shape[1]] = np.maximum(A4[Y1:Y1 + an.shape[0], X1:X1 + an.shape[1]], an)
        info.append(dict(old=old, new=new, base4=int(base), cx4=float(cx), score=round(float(sc), 3), w_old=ao.shape[1], w_new=an.shape[1]))
    A1 = cv2.resize(A4, (1920, 1080), interpolation=cv2.INTER_AREA)
    return A4, A1, info


if __name__ == '__main__':
    A4, A1, info = layers()
    for i in info: print(i)
    np.save(f'{S}/txt/l4t_a4.npy', A4); np.save(f'{S}/txt/l4t_a1.npy', A1)
