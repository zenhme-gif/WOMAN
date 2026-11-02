"""جمع أجزاء كل درس بدقة 4K وضمّ صوته من النسخة الأصلية، والتحقق من عدد الإطارات والمدة."""
import subprocess, glob, sys, os
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
SRC = {1: '/home/user/WOMAN/lessons/lesson01-taharah-wudu-ghusl.mp4', 2: '/home/user/WOMAN/lessons/lesson02-taharah-hayd-nifas.mp4',
       3: f'{S}/slides/l3.mp4', 4: '/home/user/WOMAN/lessons/lesson04-salah-jamaah.mp4'}
NAME = {1: 'lesson01-taharah-wudu-ghusl-4k.mp4', 2: 'lesson02-taharah-hayd-nifas-4k.mp4', 3: 'lesson03-salah-4k.mp4', 4: 'lesson04-salah-jamaah-4k.mp4'}
probe = lambda p, e: subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', e, '-of', 'csv=p=0', p], capture_output=True, text=True).stdout.strip()
for k in [int(x) for x in sys.argv[1:]]:
    parts = sorted(glob.glob(f'{S}/v4k/chunks/l{k}_*.mp4'))
    lst = f'{S}/v4k/chunks/list{k}.txt'
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    v = f'{S}/v4k/chunks/v{k}.mp4'; out = f'{S}/v4k/final/{NAME[k]}'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', v], check=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', v, '-i', SRC[k], '-map', '0:v', '-map', '1:a', '-c', 'copy', '-movflags', '+faststart', out], check=True)
    a = probe(SRC[k], 'stream=nb_read_packets'); b = probe(out, 'stream=nb_read_packets')
    da = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC[k]], capture_output=True, text=True).stdout.strip()
    db = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip()
    wh = probe(out, 'stream=width,height')
    print(k, 'chunks', len(parts), 'frames src', a, 'out', b, 'dur', da, db, wh, round(os.path.getsize(out) / 1e6, 1), 'MB', flush=True)
