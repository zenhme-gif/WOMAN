"""إطارات الانتقال (الخفوت العام) في الدرس: من شريط الخلفية الخالصة أعلى الإطار، بنفس معيار compose.py."""
import subprocess, numpy as np, sys, json, cv2
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
k, src = int(sys.argv[1]), sys.argv[2]
PL = cv2.imread(f'{S}/l2/plate.png')
band = PL[2:30, 300:1500].astype(np.int16)
samp = np.abs(band - np.array([228, 236, 240])).max(2) <= 1
p = subprocess.Popen(['nice', 'ffmpeg', '-loglevel', 'error', '-i', src, '-vf', 'crop=1200:28:300:2', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
flags = []
while True:
    b = p.stdout.read(1200 * 28 * 3)
    if len(b) < 1200 * 28 * 3: break
    f = np.frombuffer(b, np.uint8).reshape(28, 1200, 3).astype(np.int16)
    flags.append(float(np.median(np.abs(f[samp] - band[samp]).max(1))) >= 3)
fl = np.array(flags)
iv = []; i = 0
while i < len(fl):
    if fl[i]:
        j = i
        while j + 1 < len(fl) and fl[j + 1]: j += 1
        if iv and i - iv[-1][1] <= 5: iv[-1][1] = j
        else: iv.append([i, j])
        i = j + 1
    else: i += 1
json.dump(iv, open(f'{S}/v4k/fades{k}.json', 'w'))
print(k, len(fl), 'frames', len(iv), 'fades', int(fl.sum()), 'fade frames', iv[:5])
