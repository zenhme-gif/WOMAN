"""لكل شريحة مستخرجة: أقرب صفحة أصلية (تطابق الحبر)، والإزاحة، وما في الشريحة مما ليس في الصفحة والعكس."""
import cv2, numpy as np, glob, json
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
PL = cv2.imread(f'{S}/l2/plate.png').astype(np.int16)
CM = np.zeros((1080, 1920), bool); CM[185:1000, 60:1860] = True     # منطقة المحتوى
def page(n):
    F = cv2.imread(f'{S}/pages/{n:03d}.png'); return np.vstack([F, F[-1:]])[:1080]
PAGES = {n: page(n) for n in range(1, 144)}
def ink_page(F):
    bg = np.median(F[:40, :40].reshape(-1, 3), 0)
    return (np.abs(F.astype(np.int16) - bg).max(2) > 40) & CM
PINK = {n: ink_page(F) for n, F in PAGES.items()}
PSM = {n: cv2.resize(m.astype(np.uint8), (480, 270), interpolation=cv2.INTER_AREA) > 0 for n, m in PINK.items()}
res = {}
for k in (1, 2, 3, 4):
    for f in sorted(glob.glob(f'{S}/slides/out/درس{k}/*.png')):
        s = cv2.imread(f).astype(np.int16)
        ink = (np.abs(s - PL).max(2) > 40) & CM
        sm = cv2.resize(ink.astype(np.uint8), (480, 270), interpolation=cv2.INTER_AREA) > 0
        sc = sorted(((np.logical_and(sm, PSM[n]).sum() / max(1, np.logical_or(sm, PSM[n]).sum()), n) for n in PSM), reverse=True)[:3]
        n = sc[0][1]; P = PINK[n]
        best = None
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                Q = np.roll(np.roll(P, dy, 0), dx, 1)
                iou = np.logical_and(ink, Q).sum() / max(1, np.logical_or(ink, Q).sum())
                if best is None or iou > best[0]: best = (iou, dx, dy)
        iou, dx, dy = best
        Q = np.roll(np.roll(P, dy, 0), dx, 1)
        extra = ink & ~(cv2.dilate(Q.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
        miss = Q & ~(cv2.dilate(ink.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
        key = f'{k}/{f[-6:-4]}'
        res[key] = dict(page=n, iou=round(float(iou), 3), dx=dx, dy=dy, extra=int(extra.sum()), miss=int(miss.sum()), alt=[(round(float(a), 3), b) for a, b in sc[1:]])
        print(key, res[key], flush=True)
json.dump(res, open(f'{S}/hr/analysis.json', 'w'), ensure_ascii=False)
