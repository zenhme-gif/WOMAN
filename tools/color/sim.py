"""جيل ترميز واحد بالتحويل الافتراضي على إطارات لم تُرقَّع، لتعلّم الرجوع من «جيل واحد» إلى الأصل."""
import subprocess, numpy as np, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/l1c')
from lut import dec
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/l1c'
W, H = 1920, 1080
times = [300, 420, 520, 610, 640, 660, 900, 960, 1000]
orig = [dec(f'{S}/vcur.mp4', t).astype(np.uint8) for t in times]
print('corners orig', [tuple(np.median(f[20:60, 20:60].reshape(-1, 3), 0)) for f in orig])
enc = subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                      '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', f'{S}/sim.mp4'], input=b''.join(f.tobytes() for f in orig))
r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f'{S}/sim.mp4', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
sim = np.frombuffer(r, np.uint8).reshape(-1, H, W, 3).astype(int)
O = np.stack(orig).astype(int)
ok = np.abs(sim - O).max(-1) < 20
P, T = sim[ok], O[ok]
lut = np.zeros((3, 256))
for c in range(3):
    xs, ys = [], []
    for v in range(256):
        m = P[:, c] == v
        if m.sum() >= 30: xs.append(v); ys.append(np.median(T[m, c]))
    y = np.interp(np.arange(256), xs, ys)
    lo, hi = xs[0], xs[-1]
    y[:lo] = np.arange(lo) + (ys[0] - lo); y[hi + 1:] = np.arange(hi + 1, 256) + (ys[-1] - hi)
    lut[c] = np.maximum.accumulate(np.clip(y, 0, 255))
np.save(f'{S}/lutG1.npy', lut)
print('sim corner', tuple(np.median(sim[0, 20:60, 20:60].reshape(-1, 3), 0)))
for c in range(3): print('ch', c, [round(lut[c][v] - v, 1) for v in (20, 60, 120, 180, 220, 224, 234, 238, 250)])
c = np.stack([lut[k][sim[..., k]] for k in range(3)], -1)
print('err raw', np.abs(sim - O)[ok].mean(0).round(2), 'err fixed', np.abs(c - O)[ok].mean(0).round(2))
# التحقق على المقطعين الحقيقيين: لون الزاوية بعد التصحيح
l2 = np.load(f'{S}/lut2.npy')
for t, chain in ((690, 'A'), (805, 'B'), (840, 'B')):
    f = dec(f'{S}/vcur.mp4', t)
    g = np.stack([l2[k][f[..., k]] for k in range(3)], -1).round().astype(int) if chain == 'B' else f
    g = np.stack([lut[k][g[..., k]] for k in range(3)], -1)
    print(t, chain, 'raw', np.median(f[20:60, 20:60].reshape(-1, 3), 0), 'fixed', np.median(g[20:60, 20:60].reshape(-1, 3), 0),
          'bottom', np.median(g[1040:1075, 20:200].reshape(-1, 3), 0))
