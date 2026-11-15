"""الدرس الثاني (ورقة التعديل): وصل المجموعات الثلاث المعاد رسمها في النسخة الحالية (1080 ثم 4K)."""
import sys, os, shutil
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/splice')
import splice as SP, fadefix as FF
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
REPO = '/home/user/WOMAN/lessons/lesson02-taharah-hayd-nifas.mp4'
ORIG = f'{S}/orig_lessons/lesson02-taharah-hayd-nifas.mp4'        # إطارات الانتقال الأصلية (لقياس الخفوت)
NAME4 = 'lesson02-taharah-hayd-nifas-4k.mp4'
GROUPS = [('l2_n9', 320.5, 370.6, 371.2), ('l2_n14', 656.4, 770.867, 772.033), ('l2_n16', 807.767, 900.1, 900.667)]
n = lambda t: int(round(t * 30))
mode = sys.argv[1]
if mode == '1080':
    base = f'{S}/splice/lesson02_cur.mp4'
    if not os.path.exists(base): shutil.copy(REPO, base)
    patches = [(A, B, FF.FadedClip(f'{S}/regroup/{g}.mp4', A, ORIG, F - 0.3, B).get) for g, A, F, B in GROUPS]
    SP.run(base, patches, f'{S}/splice/lesson02_new.mp4', f'{S}/splice/w2b')
elif mode == '4kparts':
    os.makedirs(f'{S}/splice/k4_2', exist_ok=True)
    for g, A, F, B in GROUPS:
        print(f'python3 {S}/v4k/compose.py 2 {S}/splice/lesson02_new.mp4 {n(A)} {n(B)} {S}/splice/k4_2/{n(A):06d}_{n(B):06d}.mp4')
elif mode == '4k':
    SP.W, SP.H = 3840, 2160
    SP.ENC = ['-sws_flags', 'accurate_rnd+full_chroma_int+bitexact', '-c:v', 'libx264', '-preset', 'faster', '-crf', '20', '-threads', '4',
              '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360']
    base = f'{S}/v4k/prev/{NAME4}.prev2.mp4'
    if not os.path.exists(base): shutil.copy(f'{S}/v4k/final_new/{NAME4}', base)
    patches = [(A, B, SP.Clip(f'{S}/splice/k4_2/{n(A):06d}_{n(B):06d}.mp4', n(A) / 30).get) for g, A, F, B in GROUPS]
    SP.run(base, patches, f'{S}/v4k/final_new/{NAME4}', f'{S}/splice/w4k_2b')
