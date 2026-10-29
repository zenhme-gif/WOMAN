"""يطبّق تصحيح النص على مقطع فيديو مقصوص عند إطار مفتاحي، ويعيد ترميزه بإعدادات الدرس نفسها.

الاستعمال: python3 run_patch.py seg_in.mp4 seg_start seg_out.mp4
"""
import sys, subprocess, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__file__))
import patch as PT

src, t0, dst = sys.argv[1], float(sys.argv[2]), sys.argv[3]
W, H, FPS = 1920, 1080, 30
blocks = []
for b in PT.BLOCKS:
    seg_end = t0 + 60
    if b['win'][1] < t0 or b['win'][0] > t0 + 100: continue
    P = PT.prepare(b)
    blocks.append(dict(b=b, P=P, peak=False, low=0, done=False))
    print(b['name'], 'ready', flush=True)

dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360',
                        '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
i = 0
log = []
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
    t = t0 + i / FPS
    for B in blocks:
        b, P = B['b'], B['P']
        if B['done'] or not (b['win'][0] <= t <= b['win'][1]): continue
        x0, y0, x1, y1 = b['box']
        reg = fr[y0:y1, x0:x1].astype(np.float32)
        # حالة الكتلة: نسبة ظهور حبرها المشترك (لإيقاف التصحيح بعد انتهاء الانتقال)
        gd = PT.global_delta(fr)
        delta, vis = PT.fade_state(reg, P, gd)
        if vis > 0.9: B['peak'] = True
        if B['peak'] and t > b['hold'] and vis < 0.04:
            B['low'] += 1
            if B['low'] >= 3: B['done'] = True; log.append((b['name'], 'done', round(t, 2))); continue
        fr[y0:y1, x0:x1] = PT.patch_region(reg, P, gd).round().astype(np.uint8)
    enc.stdin.write(fr.tobytes())
    i += 1
enc.stdin.close(); enc.wait(); dec.wait()
print('frames', i, log, flush=True)
