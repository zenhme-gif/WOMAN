"""حالة اللوح عند لحظة معيّنة من أحداث المحرك، بلا يد (لاستخراج شريحة لا تثبت على الشاشة إلا لحظة)."""
import sys, pickle, subprocess, cv2, numpy as np
sys.path.insert(0, '.')
import render2 as R
S = R.S
t, out = float(sys.argv[1]), sys.argv[2]
ev = sorted(pickle.load(open(f'{S}/r2/events.pkl', 'rb')), key=lambda e: e[1])
T0 = 232.86667
r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{T0:.4f}', '-i', f'{S}/work/lesson2_cur.mp4', '-frames:v', '1',
                    '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
canvas = np.frombuffer(r, np.uint8).reshape(1080, 1920, 3).astype(np.float32).copy()
n = 0
for e in ev:
    if e[2] <= t: R.apply_done(canvas, e); n += 1
cv2.imwrite(out, np.clip(canvas + 0.5, 0, 255).astype(np.uint8))
print('applied', n, 'events; saved', out)
