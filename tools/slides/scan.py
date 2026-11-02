"""مسح درس منتَج لاستخراج لحظات اكتمال كل شريحة.

لكل إطار (15 إطاراً/ث بدقة مصغّرة): سطوع زاوية الإطار (يهبط مع الانتقال بين المجموعات)،
وعدد نقاط الحبر الداكن تحت اللافتة (يهبط إلى قرب الصفر حين يُمسح مربع ليُرسم الذي بعده).
الاستعمال: python3 scan.py lesson.mp4 out.npz
"""
import sys, subprocess, numpy as np

src, out = sys.argv[1], sys.argv[2]
W, H, FPS = 480, 270, 15
p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-vf', f'fps={FPS},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                     stdout=subprocess.PIPE)
corner, dark, act = [], [], []
prev = None
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.int16)
    corner.append(f[5:15, 5:15].mean())
    low = f[100:262, 20:460]
    dark.append(int((low.max(2) < 110).sum()))
    act.append(0 if prev is None else int((np.abs(f - prev).max(2) > 14).sum()))
    prev = f
np.savez(out, corner=np.array(corner), dark=np.array(dark), act=np.array(act), fps=FPS)
print(out, len(corner))
