"""جدول تصحيح لوني لكل قناة: يعيد ألوان مقطع أُعيد ترميزه إلى ألوان الأصل (انحياز التحويل إلى yuv)."""
import subprocess, numpy as np, sys
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/l1c'
def dec(p, t):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', p, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(1080, 1920, 3).astype(int)
def learn(patched, target, times):
    P = []; T = []
    for t in times:
        a, b = dec(patched, t), dec(target, t)
        ok = np.abs(a - b).max(2) < 20
        P.append(a[ok]); T.append(b[ok])
    P = np.vstack(P); T = np.vstack(T)
    lut = np.zeros((3, 256), np.float64)
    for c in range(3):
        xs, ys = [], []
        for v in range(256):
            m = P[:, c] == v
            if m.sum() >= 30: xs.append(v); ys.append(np.median(T[m, c]))
        y = np.interp(np.arange(256), xs, ys, left=np.nan, right=np.nan)
        # خارج المدى المرصود: إزاحة ثابتة مساوية لأقرب نقطة
        lo, hi = xs[0], xs[-1]
        y[:lo] = np.arange(lo) + (ys[0] - lo); y[hi + 1:] = np.arange(hi + 1, 256) + (ys[-1] - hi)
        lut[c] = np.maximum.accumulate(np.clip(y, 0, 255))
    return lut
def err(patched, target, t, lut):
    a, b = dec(patched, t), dec(target, t)
    ok = np.abs(a - b).max(2) < 20
    c = np.stack([lut[k][a[..., k]] for k in range(3)], -1)
    return np.abs(a - b)[ok].mean(0).round(2), np.abs(c - b)[ok].mean(0).round(2), b[20:60, 20:60].reshape(-1, 3).mean(0).round(1), c[20:60, 20:60].reshape(-1, 3).mean(0).round(1)
if __name__ == '__main__':
    tB = [752, 760, 770, 781, 790, 801, 812, 822, 832, 840]
    lut2 = learn(f'{S}/vcur.mp4', f'{S}/vb.mp4', tB)     # جيلان (المقطع ب)
    lut1 = learn(f'{S}/vc.mp4', f'{S}/vb.mp4', tB)       # جيل واحد
    np.save(f'{S}/lut2.npy', lut2); np.save(f'{S}/lut1.npy', lut1)
    for c in range(3): print('ch', c, 'gen1', [round(lut1[c][v] - v, 1) for v in (20, 60, 120, 180, 220, 236, 250)], 'gen2', [round(lut2[c][v] - v, 1) for v in (20, 60, 120, 180, 220, 236, 250)])
    print('check B t=805', err(f'{S}/vcur.mp4', f'{S}/vb.mp4', 805, lut2))
    print('check B(gen1) t=805', err(f'{S}/vc.mp4', f'{S}/vb.mp4', 805, lut1))
