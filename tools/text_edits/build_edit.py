"""الشرائح القياسية المتأثرة بتعديل نص صفحاتها: تُبنى من الصفحة المعدّلة (4K) كما بُنيت أصلاً،
ونسخة 1080 منها = الشريحة المستخرجة من الفيديو وقد استُبدلت منطقة السطر المعدّل بتصغير نسخة 4K."""
import sys, json, cv2, numpy as np, os
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/hr')
import build_std as B
S = B.S
A = json.load(open(f'{S}/hr/analysis.json'))
_orig = B.compose_page


def compose_edit(n, dx, dy):
    P0 = f'{S}/hr/pages4k/{n:03d}.png'; P1 = f'{S}/hr/pages4k_edit/{n:03d}.png'
    os.rename(P0, P0 + '.bak'); os.symlink(P1, P0)
    try: return _orig(n, dx, dy)
    finally: os.remove(P0); os.rename(P0 + '.bak', P0)


import sys as _s
JOBS = [tuple([int(a.split('/')[0]), a.split('/')[1]]) for a in _s.argv[1:]] or [(1, '10'), (1, '14'), (1, '27')]
for k, i in JOBS:
    v = A[f'{k}/{i}']
    s = cv2.imread(f'{S}/slides/out/درس{k}/{i}.png')
    old4 = cv2.imread(f'{S}/hr/out/درس{k}/{i}.png')
    img = compose_edit(v['page'], v['dx'], v['dy'])
    for cx, cy, r in B.find_disks(s):
        d, sc = B.digit_of(s, cx, cy, r); B.draw_disk(img, cx, cy, r, d)
    new4 = np.clip(img + 0.5, 0, 255).astype(np.uint8)
    os.makedirs(f'{S}/hr/out_edit/درس{k}', exist_ok=True)
    cv2.imwrite(f'{S}/hr/out_edit/درس{k}/{i}.png', new4, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    d4 = np.abs(new4.astype(int) - old4.astype(int)).max(2) > 12
    ys, xs = np.nonzero(d4)
    print(k, i, 'page', v['page'], '4K changed bbox', ys.min(), ys.max(), xs.min(), xs.max(), 'px', d4.sum())
    # 1080: منطقة التغيير فقط
    y0, y1, x0, x1 = ys.min() // 2 - 6, ys.max() // 2 + 7, xs.min() // 2 - 6, xs.max() // 2 + 7
    small = cv2.resize(new4, (1920, 1080), interpolation=cv2.INTER_AREA)
    s2 = s.copy(); s2[y0:y1, x0:x1] = small[y0:y1, x0:x1]
    os.makedirs(f'{S}/slides_edit/درس{k}', exist_ok=True)
    cv2.imwrite(f'{S}/slides_edit/درس{k}/{i}.png', s2)
    print('   1080 region', (y0, y1, x0, x1), 'edge diff', float(np.abs(small[y0:y1, x0:x1].astype(int) - s[y0:y1, x0:x1]).mean()))
