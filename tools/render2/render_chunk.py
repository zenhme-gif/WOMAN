import sys, pickle, subprocess, numpy as np
sys.path.insert(0, '.')
import render2 as R
S = R.S
t0, t1, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
ev = pickle.load(open(f'{S}/r2/events.pkl', 'rb'))
base = None
if len(sys.argv) > 4:      # لوح البداية: إطار الفيديو القديم عند t0 (الشريحة السابقة مكتملة)
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t0:.4f}', '-i', f'{S}/work/lesson2_cur.mp4', '-frames:v', '1',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    base = np.frombuffer(r, np.uint8).reshape(1080, 1920, 3).astype(np.float32)
R.render(ev, t0, t1, out, base=base)
print('done', out, flush=True)
