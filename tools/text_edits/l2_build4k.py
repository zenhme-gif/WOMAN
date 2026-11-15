"""الدرس الثاني: شرائح 4K للشرائح الجديدة (بعد ورقة التعديل)، من الصفحات المعدّلة كما بُنيت الشرائح القياسية أصلاً،
والأقراص وأرقامها من شريحة 1080 الجديدة."""
import sys, json, cv2, numpy as np, os
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/hr')
import build_std as B
S = B.S
A = json.load(open(f'{S}/hr/analysis.json'))
_orig = B.compose_page


def compose_edit(n, dx, dy):
    P0 = f'{S}/hr/pages4k/{n:03d}.png'; P1 = f'{S}/hr/pages4k_edit/{n:03d}.png'
    if not os.path.exists(P1): return _orig(n, dx, dy)
    os.rename(P0, P0 + '.bak'); os.symlink(P1, P0)
    try: return _orig(n, dx, dy)
    finally: os.remove(P0); os.rename(P0 + '.bak', P0)


NEW = {14: '2/14', 15: '2/15', 25: '2/28', 26: '2/29', 29: '2/32', 30: '2/33', 31: '2/35'}     # الشريحة الجديدة ← مفتاح الأصل (الصفحة والإزاحة)
PAGE = {14: 58, 15: 59, 25: 72, 26: 73, 29: 77, 30: 78, 31: 80}
for k, key in NEW.items():
    v = A[key]
    s = cv2.imread(f'{S}/slides/out/درس2/{k:02d}.png')
    img = compose_edit(PAGE[k], v['dx'], v['dy'])
    disks = B.find_disks(s)
    for cx, cy, r in disks:
        d, sc = B.digit_of(s, cx, cy, r); B.draw_disk(img, cx, cy, r, d)
    out = np.clip(img + 0.5, 0, 255).astype(np.uint8)
    cv2.imwrite(f'{S}/hr/out/درس2/{k:02d}.png', out, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    mean, bad = B.verify(img, s)
    print(k, 'page', PAGE[k], 'disks', [(cx, cy, B.digit_of(s, cx, cy, r)[0]) for cx, cy, r in disks], 'verify mean %.2f bad %d' % (mean, bad), flush=True)
