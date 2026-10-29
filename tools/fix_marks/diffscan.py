"""مسح كل الإطارات: عدد النقاط المتغيرة بوضوح (>40) داخل مناطق التصحيح وخارجها."""
import sys, subprocess, numpy as np
sys.path.insert(0, '.')
import patch as PT
a, b, t0 = sys.argv[1], sys.argv[2], float(sys.argv[3])
W, H = 1920, 1080
pa = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-ss', f'{t0:.3f}', '-i', a, '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
pb = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', b, '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
inside = np.zeros((H, W), bool)
for bl in PT.BLOCKS:
    x0, y0, x1, y1 = bl['box']; inside[y0:y1, x0:x1] = True
i = 0; worst_out = []; ins = []
while True:
    x = pa.stdout.read(W * H); y = pb.stdout.read(W * H)
    if len(y) < W * H or len(x) < W * H: break
    d = np.abs(np.frombuffer(x, np.uint8).astype(int) - np.frombuffer(y, np.uint8).astype(int)).reshape(H, W) > 40
    worst_out.append(int(d[~inside].sum())); ins.append(int(d[inside].sum())); i += 1
wo = np.array(worst_out); ii = np.array(ins)
print(f'frames {i}  outside>40: max {wo.max()} (frame {wo.argmax()}, t={t0 + wo.argmax()/30:.2f})  inside: median {np.median(ii):.0f} max {ii.max()} at t={t0 + ii.argmax()/30:.2f}')
top = np.argsort(ii)[-5:][::-1]; print('  top inside:', [(round(t0 + k / 30, 2), int(ii[k])) for k in top])
