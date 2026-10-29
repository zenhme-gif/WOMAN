"""طاقة نطاقات التردد نسبةً إلى 300–3000 هرتز، وأرضية الضوضاء وقمة الكلام (إطارات 50 ملّي ثانية)."""
import sys, subprocess, numpy as np
def load(p, ss, t, sr=48000):
    a = ['ffmpeg', '-loglevel', 'error', '-ss', str(ss), '-t', str(t), '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(a, capture_output=True).stdout, np.float32)
p, ss, t = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
x = load(p, ss, t); sr = 48000
F = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; f = np.fft.rfftfreq(len(x), 1 / sr)
ref = F[(f > 300) & (f < 3000)].sum()
bands = [(50, 100), (100, 300), (3000, 5000), (5000, 8000), (8000, 12000), (12000, 16000)]
fr = x[:len(x) // 2400 * 2400].reshape(-1, 2400); e = 10 * np.log10((fr ** 2).mean(1) + 1e-12)
print(p.split('/')[-1][:28].ljust(28), ' '.join(f'{a}-{b}:{10*np.log10(F[(f>a)&(f<b)].sum()/ref):6.1f}' for a, b in bands),
      f' floor {np.percentile(e,10):6.1f} peak {np.percentile(e,95):6.1f} clip {(np.abs(x)>0.97).mean()*100:.3f}%')
