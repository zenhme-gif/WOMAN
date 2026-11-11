"""الدرس الرابع 4K: وصل مقطع «موضوعات الدرس» المبني بدقة 4K من نسخة 1080 المرقّعة، في النسخة الحالية final_new."""
import sys, os, shutil
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/splice')
import splice as SP, lesson as L
S = L.S
N0, N1 = 536, 806
SP.W, SP.H = 3840, 2160
SP.ENC = ['-sws_flags', 'accurate_rnd+full_chroma_int+bitexact', '-c:v', 'libx264', '-preset', 'faster', '-crf', '20', '-threads', '4',
          '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360']
base = f'{S}/v4k/final_new/{L.NAME4[4]}.prev.mp4'
if not os.path.exists(base): shutil.copy(f'{S}/v4k/final_new/{L.NAME4[4]}', base)
c = SP.Clip(f'{S}/splice/k4_4/{N0:06d}_{N1:06d}.mp4', N0 / 30)
SP.run(base, [(N0 / 30, N1 / 30, c.get)], f'{S}/v4k/final_new/{L.NAME4[4]}', f'{S}/splice/w4k_4t')
