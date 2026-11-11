"""توقيت كتابة منطقة نص في الأصل: عدد نقاط الحبر المطابقة للشريحة النهائية في المنطقة، إطاراً إطاراً.
python3 linetime.py video t0 t1 slide.png y0 y1 x0 x1"""
import sys, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/regroup')
import sched as SC
v, t0, t1, sl = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
y0, y1, x0, x1 = map(int, sys.argv[5:9])
ref = cv2.imread(sl)[y0:y1, x0:x1].astype(np.int16)
m = (ref.max(2) < 110) & ((ref.max(2) - ref.min(2)) < 40)
PL = SC.R.PLATE.astype(np.int16)
out = []
for i, f in enumerate(SC.stream(v, t0, t1)):
    r = f[y0:y1, x0:x1].astype(np.int16)
    c = int((np.abs(r[m] - ref[m]).max(1) < 35).sum())
    red = int(((f[60:440, 200:1720, 2] > 180) & (f[60:440, 200:1720, 1] < 130) & (f[60:440, 200:1720, 0] < 140)).sum())
    hand = int((np.abs(f.astype(np.int16) - PL).max(2) > 60)[:, :].sum())
    out.append((t0 + i / 30, c, red))
tot = m.sum(); print('mask px', tot)
for t, c, red in out[::6]: print(f'{t:7.2f} {c:6d} {c/tot:5.2f} red {red}')
