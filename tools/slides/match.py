"""أي شريحة أصلية على الشاشة في كل لحظة: مطابقة منطقة الصندوق مع الصفحات الـ143 (إطاران في الثانية)."""
import sys, subprocess, numpy as np, cv2, json
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
src, out = sys.argv[1], sys.argv[2]
X0, Y0, X1, Y1 = 600, 490, 1312, 690
def norm(g): g = g.astype(np.float32); return (g - g.mean()) / (g.std() + 1e-6)
pages = {}
for n in range(1, 144):
    p = cv2.imread(f'{S}/pages/{n:03d}.png'); p = np.vstack([p, p[-1:]])
    pages[n] = norm(cv2.cvtColor(cv2.resize(p[Y0:Y1, X0:X1], None, fx=0.5, fy=0.5), cv2.COLOR_BGR2GRAY))
keys = list(pages); stack = np.stack([pages[k] for k in keys]).reshape(len(keys), -1)
p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-vf', 'fps=2', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
res = []; t = 0.0
while True:
    b = p.stdout.read(1920 * 1080 * 3)
    if len(b) < 1920 * 1080 * 3: break
    f = np.frombuffer(b, np.uint8).reshape(1080, 1920, 3)
    g = norm(cv2.cvtColor(cv2.resize(f[Y0:Y1, X0:X1], None, fx=0.5, fy=0.5), cv2.COLOR_BGR2GRAY)).ravel()
    sc = stack @ g / g.size
    i = int(np.argmax(sc)); res.append((round(t, 2), keys[i], round(float(sc[i]), 3))); t += 0.5
json.dump(res, open(out, 'w'))
print(out, len(res))
