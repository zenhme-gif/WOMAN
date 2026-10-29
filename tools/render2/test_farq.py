import sys, time, cv2, numpy as np
sys.path.insert(0, '.')
import render2 as R
S = R.S
F1 = cv2.imread(f'{S}/r2/steps/farq_1.png'); F2 = cv2.imread(f'{S}/r2/steps/farq_2.png')
bg = np.median(F1[:40, :40].reshape(-1, 3), 0).astype(np.float32)
t = time.time()
hd = R.Header(F1, bg); it1 = R.Item(F1, bg, 1); it2 = R.Item(F2, bg, 2)
print('elements', round(time.time() - t, 1), 's; lines', len(it1.lines), len(it2.lines), 'boxtext', len(it1.boxtext), len(it2.boxtext))
tl = R.Timeline(262.0)
R.plan_group(tl, hd, [it1, it2], [263.5, 271.5], 290.4)
for e in tl.ev:
    if e[0] in ('draw', 'fade', 'clear'): print(e[0], round(e[1], 2), round(e[2], 2))
t = time.time()
R.render(tl.ev, 286.0, 296.5, f'{S}/r2/test_farq.mp4', audio=f'{S}/work/lesson2_cur.mp4')
print('render', round(time.time() - t, 1), 's')
