"""تجميع الدرس الثاني: ما قبل «الفرق» منسوخ كما هو، ثم المقاطع الجديدة، ثم الخاتمة بانتقال مصحَّح من الإطار الجديد."""
import subprocess, numpy as np, os
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
CUR = f'{S}/work/lesson2_cur.mp4'; W, H = 1920, 1080
os.makedirs(f'{S}/r2/seg', exist_ok=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', CUR, '-map', '0:v', '-c', 'copy', '-f', 'segment',
                '-segment_times', '261.12,1063.35', '-reset_timestamps', '1', '-segment_format', 'mp4', f'{S}/r2/seg/s%d.mp4'], check=True)
def frames(p):
    pr = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    while True:
        b = pr.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
def last_frame(p):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-sseof', '-0.1', '-i', p, '-update', '1', '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8)[-W * H * 3:].reshape(H, W, 3).astype(np.float32)
old_last = last_frame(f'{S}/r2/seg/s1.mp4')
new_last = last_frame(f'{S}/r2/c3.mp4')
# وزن الإطار الأخير في كل إطار من انتقال الخاتمة: من منطقة اللافتة (حمراء في الدرس، خلفية في الشعار)
outro = list(frames(f'{S}/r2/seg/s2.mp4'))
ref = outro[min(30, len(outro) - 1)]                      # الشعار بعد انتهاء الانتقال
m = (np.abs(old_last - ref).max(2) > 60)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', f'{S}/r2/seg/s2fix.mp4'], stdin=subprocess.PIPE)
ws = []
for k, f in enumerate(outro):
    w = float(np.clip(np.median(((f - ref) / (old_last - ref + 1e-3))[m]), 0, 1)) if k < 25 else 0.0
    ws.append(round(w, 2))
    g = f + (new_last - old_last) * w
    enc.stdin.write(np.clip(g, 0, 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()
print('outro weights', ws[:22])
open(f'{S}/r2/seg/list.txt', 'w').write(''.join(f"file '{p}'\n" for p in
    [f'{S}/r2/seg/s0.mp4', f'{S}/r2/c1.mp4', f'{S}/r2/c2.mp4', f'{S}/r2/c3.mp4', f'{S}/r2/seg/s2fix.mp4']))
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{S}/r2/seg/list.txt', '-c', 'copy', f'{S}/r2/v.mp4'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'{S}/r2/v.mp4', '-i', CUR, '-map', '0:v', '-map', '1:a', '-c', 'copy',
                '-movflags', '+faststart', '/home/user/WOMAN/lessons/lesson02-taharah-hayd-nifas.mp4'], check=True)
for p in (f'{S}/r2/seg/s0.mp4', f'{S}/r2/c1.mp4', f'{S}/r2/c2.mp4', f'{S}/r2/c3.mp4', f'{S}/r2/seg/s2fix.mp4', CUR, '/home/user/WOMAN/lessons/lesson02-taharah-hayd-nifas.mp4'):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', p], capture_output=True, text=True).stderr
    print(p.split('/')[-1], [l.strip() for l in out.splitlines() if 'Duration' in l][0][:22])
