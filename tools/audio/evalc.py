"""تقييم سلسلة تنقية: أرضية السكتات، ووضوح الحروف (طاقة 4–8 ك هرتز في إطارات الكلام نسبةً إلى 300–3000)."""
import sys, subprocess, numpy as np
def load(p, sr=48000):
    a = ['ffmpeg', '-loglevel', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.float32)
def stats(x, sr=48000, n=2400):
    fr = x[:len(x) // n * n].reshape(-1, n)
    e = 10 * np.log10((fr ** 2).mean(1) + 1e-12)
    S = np.abs(np.fft.rfft(fr * np.hanning(n), axis=1)) ** 2; f = np.fft.rfftfreq(n, 1 / sr)
    sp = e > np.percentile(e, 60)
    mid = S[sp][:, (f > 300) & (f < 3000)].sum(1); hi = S[sp][:, (f > 4000) & (f < 8000)].sum(1); air = S[sp][:, (f > 8000) & (f < 14000)].sum(1)
    return np.percentile(e, 10), np.percentile(e, 95), 10 * np.log10(np.median(hi / mid)), 10 * np.log10(np.median(air / mid))
for p in sys.argv[1:]:
    fl, pk, hi, air = stats(load(p))
    print(f'{p:26s} floor {fl:6.1f}  peak {pk:6.1f}  snr {pk-fl:5.1f}  clarity(4-8k) {hi:6.1f}  air(8-14k) {air:6.1f}')
