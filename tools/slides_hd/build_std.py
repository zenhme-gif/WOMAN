"""الشرائح القياسية بدقة 3840×2160: اللوح العالي الدقة + الصفحة الأصلية (من 15364×8636) + أقراص الأرقام مرسومة من جديد.
يُتحقق من كل شريحة بتصغيرها إلى 1080 ومقارنتها بالشريحة المستخرجة من الفيديو."""
import cv2, numpy as np, json, sys, os
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
FONT = '/root/.claude/skills/synced/3677d22d-6e71-479f-845a-4326e7166740_f78b016c-697b-4b0f-bf6a-496e8efb78cc/hdat-identity/assets/fonts/Tajawal-Bold.ttf'
DISK_YEL = (97, 210, 237); DIGIT_BLUE = (123, 75, 7)          # BGR كما في المحرك
AR = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
PLATE4 = cv2.imread(f'{S}/hr/plate4k.png').astype(np.float32)
PL1 = cv2.imread(f'{S}/l2/plate.png').astype(np.int16)
os.makedirs(f'{S}/hr/out', exist_ok=True)


def find_disks(s):
    f = s.astype(int); B, G, R = f[..., 0], f[..., 1], f[..., 2]
    yel = ((R > 190) & (G > 160) & (R - B > 70)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(yel)
    out = []
    for j in range(1, n):
        x, y, w, h, a = st[j]
        if 40 <= w <= 95 and 0.8 < w / h < 1.25 and a > 0.45 * w * h and y > 150:
            out.append((x + w / 2.0, y + h / 2.0, w / 2.0))
    return out


_digit_cache = {}
def digit_of(s, cx, cy, r):
    """الرقم في القرص: مطابقة شكل الحبر الأزرق داخله برسوم الأرقام ١–٩."""
    x0, y0 = int(cx - r), int(cy - r); crop = s[y0:y0 + int(2 * r), x0:x0 + int(2 * r)].astype(int)
    m = ((crop[..., 0] - crop[..., 2]) > 40).astype(np.float32)
    best = None
    for d in range(1, 10):
        key = (d, int(round(r)))
        if key not in _digit_cache:
            im = Image.new('L', (crop.shape[1], crop.shape[0]), 0); dr = ImageDraw.Draw(im)
            dr.text((crop.shape[1] / 2, crop.shape[0] / 2 + 3), str(d).translate(AR), font=ImageFont.truetype(FONT, int(r * 1.3)), fill=255, anchor='mm')
            _digit_cache[key] = np.asarray(im).astype(np.float32) / 255
        t = _digit_cache[key]
        if t.shape != m.shape: t = cv2.resize(t, (m.shape[1], m.shape[0]))
        best_d = max(cv2.matchTemplate(cv2.copyMakeBorder(m, 6, 6, 6, 6, cv2.BORDER_CONSTANT), t, cv2.TM_CCOEFF_NORMED).max(), -1)
        if best is None or best_d > best[0]: best = (best_d, d)
    return best[1], best[0]


def draw_disk(img4, cx, cy, r, d):
    """قرص أصفر ورقم أزرق بدقة 4K (رسم بأربعة أضعاف ثم تصغير لنعومة الحواف)."""
    SS = 4; R4 = 2 * r; size = int(np.ceil(2 * R4 + 8))
    big = Image.new('RGBA', (size * SS, size * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(big)
    c = size * SS / 2
    dr.ellipse([c - R4 * SS, c - R4 * SS, c + R4 * SS, c + R4 * SS], fill=DISK_YEL[::-1] + (255,))
    dr.text((c, c + 6 * SS), str(d).translate(AR), font=ImageFont.truetype(FONT, int(r * 1.3 * 2 * SS)), fill=DIGIT_BLUE[::-1] + (255,), anchor='mm')
    sm = np.asarray(big.resize((size, size), Image.LANCZOS)).astype(np.float32)
    rgb = sm[..., 2::-1]; a = sm[..., 3:] / 255.0
    X0 = int(round(2 * cx - size / 2)); Y0 = int(round(2 * cy - size / 2))
    reg = img4[Y0:Y0 + size, X0:X0 + size]
    reg[:] = rgb * a + reg * (1 - a)


def compose_page(n, dx, dy):
    P = cv2.imread(f'{S}/hr/pages4k/{n:03d}.png').astype(np.float32)
    if dx or dy: P = np.roll(np.roll(P, 2 * dy, 0), 2 * dx, 1)
    pbg = np.median(P[:80, :80].reshape(-1, 3), 0)
    # داخل الصناديق أبيض في الصفحات، وفي الفيديو بلون اللوح: يُعامل الأبيض الواسع خلفيةً كذلك
    wh = (P.min(2) >= 250).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(wh, 4)
    big = np.isin(lab, [j for j in range(1, n) if st[j, 4] > 60000 and st[j, 2] > 200 and st[j, 3] > 100])
    from scipy import ndimage as ndi
    inner = ndi.binary_fill_holes(big)
    ref = np.where(inner[..., None], np.float32(255), pbg.astype(np.float32))
    a = np.clip(np.abs(P - ref).max(2) / 60.0, 0, 1)[..., None]
    return P + (PLATE4 - ref) * (1 - a)


def verify(img4, s):
    small = cv2.resize(np.clip(img4, 0, 255).astype(np.uint8), (1920, 1080), interpolation=cv2.INTER_AREA).astype(int)
    d = np.abs(small - s.astype(int)).max(2)
    big = cv2.morphologyEx((d > 60).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return float(d.mean()), int(big.sum())


if __name__ == '__main__':
    A = json.load(open(f'{S}/hr/analysis.json'))
    skip = set(sys.argv[1:])
    rep = {}
    for key, v in sorted(A.items()):
        if v['iou'] < 0.9 or v['miss'] > 4000 or v['extra'] > 10000 or key in skip: continue
        k, i = key.split('/')
        s = cv2.imread(f'{S}/slides/out/درس{k}/{i}.png')
        img = compose_page(v['page'], v['dx'], v['dy'])
        disks = []
        for cx, cy, r in find_disks(s):
            d, sc = digit_of(s, cx, cy, r); disks.append((round(cx, 1), round(cy, 1), r, d, round(float(sc), 2)))
            draw_disk(img, cx, cy, r, d)
        mean, bad = verify(img, s)
        os.makedirs(f'{S}/hr/out/درس{k}', exist_ok=True)
        cv2.imwrite(f'{S}/hr/out/درس{k}/{i}.png', np.clip(img + 0.5, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 6])
        rep[key] = dict(page=v['page'], disks=disks, diff_mean=round(mean, 2), diff_px=bad)
        print(key, rep[key], flush=True)
    json.dump(rep, open(f'{S}/hr/std_report.json', 'w'), ensure_ascii=False)
