"""إزاحة ملف b عن المرجع a (موجب = b متأخر) بالارتباط المتبادل في عدة مواضع، بعد فلتر 200–3000 هرتز."""
import sys, subprocess, numpy as np
def ld(p, ss, t, sr=8000):
    a = ['ffmpeg', '-loglevel', 'error', '-ss', str(max(ss, 0)), '-t', str(t), '-i', p, '-ac', '1', '-ar', str(sr), '-af', 'highpass=f=200,lowpass=f=3000', '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.float32)
a, b, shift, end = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])   # b(t + shift) ≈ a(t)
for t in np.linspace(30, end - 40, 6):
    x = ld(a, t, 20); y = ld(b, t + shift - 1, 22)
    c = np.correlate(y - y.mean(), x - x.mean(), 'valid')
    print(f'{t:6.0f}s: {(np.argmax(c) - 8000) / 8:+.2f} ms   r={c.max()/np.sqrt((x**2).sum()*(y[:len(x)]**2).sum()+1e-9):.2f}')
