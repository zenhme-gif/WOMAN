"""الصفحات الأصلية (15364×8636) مصغّرة إلى 3840×2160 بمتوسط المساحة، والصف الأخير مكرر كما في الفيديو."""
import sys, glob, cv2, numpy as np, os
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
part, nparts = int(sys.argv[1]), int(sys.argv[2])
fs = sorted(glob.glob(f'{S}/rar_src/*/*.png'))
for i, f in enumerate(fs):
    if i % nparts != part: continue
    n = int(f.rsplit('_', 1)[1][:3]); out = f'{S}/hr/pages4k/{n:03d}.png'
    if os.path.exists(out): continue
    a = cv2.imread(f, cv2.IMREAD_COLOR)
    b = cv2.resize(a, (3840, 2159), interpolation=cv2.INTER_AREA)
    b = np.vstack([b, b[-1:]])
    cv2.imwrite(out, b, [cv2.IMWRITE_PNG_COMPRESSION, 3])
    print(n, flush=True)
