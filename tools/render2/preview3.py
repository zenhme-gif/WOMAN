import sys, cv2, numpy as np
sys.path.insert(0, '.')
import render2 as R
S = R.S
outs = []
for name in ('farq', 'tawaf', 'mushaf'):
    F1 = cv2.imread(f'{S}/r2/steps/{name}_1.png'); F2 = cv2.imread(f'{S}/r2/steps/{name}_2.png')
    bg = np.median(F1[:40, :40].reshape(-1, 3), 0).astype(np.float32)
    hd = R.Header(F1, bg); it = [R.Item(F1, bg, 1), R.Item(F2, bg, 2)]
    tl = R.Timeline(0.0); R.plan_group(tl, hd, it, [1.0, 15.0], 60.0, next_exists=False)
    t_end = tl.t + 0.5
    R.render(tl.ev, t_end, t_end + 1 / 30, f'{S}/r2/p_{name}.mp4')
    outs.append(f'{S}/r2/p_{name}.mp4')
print(outs)
