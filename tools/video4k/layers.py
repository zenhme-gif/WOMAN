"""طبقات كل شريحة بدقة 4K كما تظهر في الفيديو: مكتملة التلوين، وقبل التلوين (لافتة بحدّ أحمر ونص مفرَّغ، وقرص حلقة)،
بلون نص الشرح الذي في الفيديو."""
import cv2, numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/hr')
import build_std as B
from scipy import ndimage as ndi
S = B.S
PLATE4 = cv2.imread(f'{S}/hr/plate4k.png')
PLATE1 = cv2.imread(f'{S}/l2/plate.png')
RED_LINE = np.array([94, 95, 213], np.float32)
RING = np.array(B.DISK_YEL, np.float32)


def items(k):
    return json.load(open(f'{S}/slides/out/درس{k}.json'))


def recolor_text(T4, T1):
    """نص الشرح الداكن بلون الفيديو (رمادي في الإخراج القديم، أسود في الجديد)."""
    def dark_col(img, lo):
        f = img.astype(np.int16); L = f.mean(2); sat = f.max(2) - f.min(2)
        m = (L < 110) & (sat < 30); m[:lo] = False
        return np.median(img[m].reshape(-1, 3), 0) if m.sum() > 50 else None
    cv_ = dark_col(T1, 420); c4 = dark_col(T4, 840)
    if cv_ is None or c4 is None or np.abs(cv_ - c4).max() < 12: return T4
    f = T4.astype(np.float32); L = f.mean(2); sat = f.max(2) - f.min(2)
    Lbg = PLATE4.astype(np.float32).mean(2)
    a = np.clip((Lbg - L) / np.maximum(Lbg - c4.mean(), 1), 0, 1)
    m = (sat < 40) & (a > 0.02); m[:840] = False
    a = np.where(m, a, 0)[..., None]
    out = f * (1 - a) + (PLATE4 * (1 - a) + cv_.astype(np.float32) * a) * (a > 0) * 1.0 + 0
    out = np.where(m[..., None], PLATE4 * (1 - a) + cv_.astype(np.float32) * a, f)
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def unfilled(T4, disks):
    """اللافتة قبل التلوين: حدّ أحمر رفيع ونص العنوان مفرَّغاً، والقرص حلقة صفراء ورقمه."""
    f = T4.astype(np.int16); out = T4.astype(np.float32).copy()
    red = (f[..., 2] > 150) & (f[..., 2] - f[..., 0] > 60) & (f[..., 2] - f[..., 1] > 50); red[900:] = False
    n, lab, st, _ = cv2.connectedComponentsWithStats(red.astype(np.uint8))
    if n > 1:
        j = 1 + int(np.argmax(st[1:, 4])); Bm = ndi.binary_fill_holes(lab == j)
        txt = Bm & (f.min(2) > 180)
        ring = Bm & ~(cv2.erode(Bm.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
        tr = (cv2.dilate(txt.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0) & ~(cv2.erode(txt.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
        Bd = cv2.dilate(Bm.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        out[Bd] = PLATE4[Bd]
        # الخطوط الرفيعة (حدّ اللافتة والنص المفرَّغ) تُترك للإطار نفسه: تُكبَّر منه ولا تُركَّب
    for cx, cy, r, d in disks:
        X, Y = 2 * cx, 2 * cy; R = 2 * r
        yy, xx = np.ogrid[:2160, :3840]; dd = np.sqrt((yy - Y) ** 2 + (xx - X) ** 2)
        inside = dd < R + 3
        blue = (f[..., 0] - f[..., 2] > 40) & inside
        keep = out[blue].copy()
        out[inside] = PLATE4[inside]
        out[blue] = keep                                     # الرقم وحده؛ الحلقة الرفيعة تُكبَّر من الإطار
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def item_layers(k, idx, it):
    """(مكتملة، قبل التلوين) بدقة 4K لشريحة رقمها idx (1..)."""
    T4 = cv2.imread(f'{S}/hr/out/درس{k}/{idx:02d}.png')
    T1 = cv2.imread(f'{S}/slides/out/درس{k}/{idx:02d}.png')
    # محاذاة دون البكسل: الإخراج القديم مزاح نصف بكسل عن الصفحة (يُصحَّح بكسلاً في 4K)
    g1 = cv2.cvtColor(T1[420:1000, 300:1620], cv2.COLOR_BGR2GRAY).astype(np.float32)
    g2 = cv2.cvtColor(cv2.resize(T4, (1920, 1080), interpolation=cv2.INTER_AREA)[420:1000, 300:1620], cv2.COLOR_BGR2GRAY).astype(np.float32)
    (sx, sy), resp = cv2.phaseCorrelate(g1, g2)
    dx4, dy4 = -int(round(2 * sx)), -int(round(2 * sy))
    if resp > 0.3 and (dx4 or dy4) and abs(dx4) <= 4 and abs(dy4) <= 4:
        T4 = np.roll(np.roll(T4, dy4, 0), dx4, 1)
    disks = []
    for cx, cy, r in B.find_disks(T1):
        d, _ = B.digit_of(T1, cx, cy, r); disks.append((cx, cy, r, d))
    if (k, idx) == (1, 17): disks = [(cx, 449.0, 38.5, d) for cx, cy, r, d in disks]
    return T4, unfilled(T4, disks)
