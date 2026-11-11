"""وصل المقدمة المصححة (بلا ظل اسم الشيخ) في نسخة 4K: python3 intro_splice.py K"""
import sys, os, shutil
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/splice')
import splice as SP
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
NAME4 = {1: 'lesson01-taharah-wudu-ghusl-4k.mp4', 2: 'lesson02-taharah-hayd-nifas-4k.mp4', 3: 'lesson03-salah-4k.mp4', 4: 'lesson04-salah-jamaah-4k.mp4'}
END = {1: 825, 2: 585, 3: 825, 4: 465}
SP.W, SP.H = 3840, 2160
SP.ENC = ['-sws_flags', 'accurate_rnd+full_chroma_int+bitexact', '-c:v', 'libx264', '-preset', 'faster', '-crf', '20', '-threads', '4',
          '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360']
k = int(sys.argv[1])
src = f'{S}/v4k/final_new/{NAME4[k]}'
if not os.path.exists(src): src = f'{S}/v4k/final/{NAME4[k]}'
tmp = f'{S}/v4k/final_new/{NAME4[k]}.intro.mp4'
c = SP.Clip(f'{S}/splice/intro4k/l{k}.mp4', 0)
SP.run(src, [(0, END[k] / 30, c.get)], tmp, f'{S}/splice/wi{k}')
os.replace(tmp, f'{S}/v4k/final_new/{NAME4[k]}')
print('ok', k)
