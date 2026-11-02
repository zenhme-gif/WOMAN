"""إعادة لون اللوح في مقطعَي الدرس الأول المرقَّعين إلى لون بقية الدرس.
المقطع أ (675.75–717.42) أُعيد ترميزه مرة فأُعتم 4 درجات، والمقطع ب (750.75–842.42) مرتين فأُعتم 7.
يُقطع الدرس عند الإطارات المفتاحية، ويُصحَّح كل مقطع بجدوله ثم يُرمَّز بتحويل دقيق، ويُجمع الكل بالنسخ."""
import subprocess, numpy as np, os
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/l1c'
SRC = f'{S}/vcur.mp4'; W, H = 1920, 1080
os.makedirs(f'{S}/seg', exist_ok=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', SRC, '-map', '0:v', '-c', 'copy', '-f', 'segment', '-segment_times', '675.70,717.40,750.70,842.40',
                '-reset_timestamps', '1', '-segment_format', 'mp4', f'{S}/seg/s%d.mp4'], check=True)
G1 = np.load(f'{S}/lutG1.npy')                       # جيل واحد ← الأصل (من ترميز تجريبي لإطارات لم تُرقَّع)
L2 = np.round(np.load(f'{S}/lut2.npy')).astype(int)   # ثلاثة أجيال ← جيل واحد (من مقارنة نسختين في المستودع)
lut = {1: G1, 3: np.stack([G1[c][L2[c]] for c in range(3)])}
for k, L in lut.items():
    L8 = np.clip(np.round(L), 0, 255).astype(np.uint8)
    dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', f'{S}/seg/s{k}.mp4', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', '30', '-i', '-',
                            '-sws_flags', 'accurate_rnd+full_chroma_int+bitexact', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                            '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360', f'{S}/seg/s{k}c.mp4'], stdin=subprocess.PIPE)
    n = 0
    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        g = np.stack([L8[c][f[..., c]] for c in range(3)], -1)
        enc.stdin.write(g.tobytes()); n += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print('segment', k, 'frames', n, flush=True)
open(f'{S}/seg/list.txt', 'w').write(''.join(f"file '{S}/seg/{x}.mp4'\n" for x in ('s0', 's1c', 's2', 's3c', 's4')))
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{S}/seg/list.txt', '-c', 'copy', f'{S}/v.mp4'], check=True)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'{S}/v.mp4', '-i', SRC, '-map', '0:v', '-map', '1:a', '-c', 'copy', '-movflags', '+faststart',
                f'{S}/lesson1_fixed.mp4'], check=True)
for p in (SRC, f'{S}/lesson1_fixed.mp4'):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', p], capture_output=True, text=True).stderr
    print(p.split('/')[-1], [l.strip() for l in out.splitlines() if 'Duration' in l][0][:22])
