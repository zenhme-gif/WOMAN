"""وصل تعديلات درس: python3 lesson.py K 1080 | python3 lesson.py K 4k
1080: الأصل + المقاطع المعاد رسمها (بانتقال الأصل نفسه) ← lessonK_new.mp4
4k: تُبنى بدقة 4K إطارات المقاطع المعدّلة وحدها من نسخة 1080 الجديدة، ثم توصل بنسخة 4K الحالية."""
import sys, os, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/splice')
import splice as SP, fadefix as FF
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
SRC = {1: '/home/user/WOMAN/lessons/lesson01-taharah-wudu-ghusl.mp4', 3: f'{S}/slides/l3.mp4', 4: '/home/user/WOMAN/lessons/lesson04-salah-jamaah.mp4'}
NAME4 = {1: 'lesson01-taharah-wudu-ghusl-4k.mp4', 3: 'lesson03-salah-4k.mp4', 4: 'lesson04-salah-jamaah-4k.mp4'}
GROUPS = {   # (المقطع، A، بدء انتقال الأصل F، نهايته B)
    1: [('l1_e1', 465.9333, 615.3667, 616.3667), ('l1_e2', 643.7333, 674.6667, 675.3333), ('l1_e3', 675.3, 711.8667, 712.4333),
        ('l1_e4', 780.2, 837.6333, 838.5667), ('l1_e5', 975.5333, 1082.3, 1083.3)],
    3: [('l3_e6', 958.0667, 1032.3, 1033.3)],
    4: [('l4_g1', 27.3333, 69.4333, 70.4667), ('l4_g4', 344.2, 514.9, 515.9333), ('l4_g5', 515.9333, 658.7, 659.7333), ('l4_g6', 659.7333, 734.4, 735.4333)],
}
n = lambda t: int(round(t * 30))


def ranges(k):
    out = []; prev = 0
    if k == 1:
        import intro_mark as IM
        im = IM.IntroMark(); out.append((im.n0, im.n1, im.get, None))
    for name, A, F, B in GROUPS[k]:
        a = max(n(A), prev); b = n(B); prev = b
        out.append((a, b, FF.FadedClip(f'{S}/regroup/{name}.mp4', A, SRC[k], F - 0.3, B).get, name))
    return out


if __name__ == '__main__':
    k, mode = int(sys.argv[1]), sys.argv[2]
    new1080 = f'{S}/splice/lesson{k:02d}_new.mp4'
    if mode == '1080':
        SP.run(SRC[k], [(a, b, g) for a, b, g, _ in ranges(k)], new1080, f'{S}/splice/w{k}')
    elif mode == '4kparts':
        os.makedirs(f'{S}/splice/k4_{k}', exist_ok=True)
        jobs = []
        for a, b, _, name in ranges(k):
            out = f'{S}/splice/k4_{k}/{a:06d}_{b:06d}.mp4'
            jobs.append(f'python3 {S}/v4k/compose.py {k} {new1080} {a} {b} {out} > {out}.log 2>&1')
        open(f'{S}/splice/k4_{k}/jobs.sh', 'w').write('\n'.join(jobs) + '\n')
        print('\n'.join(jobs))
    elif mode == '4k':
        SP.W, SP.H = 3840, 2160
        SP.ENC = ['-sws_flags', 'accurate_rnd+full_chroma_int+bitexact', '-c:v', 'libx264', '-preset', 'faster', '-crf', '20', '-threads', '4',
                  '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360']
        patches = []
        for a, b, _, name in ranges(k):
            c = SP.Clip(f'{S}/splice/k4_{k}/{a:06d}_{b:06d}.mp4', a / 30)
            patches.append((a, b, c.get))
        os.makedirs(f'{S}/v4k/final_new', exist_ok=True)
        SP.run(f'{S}/v4k/final/{NAME4[k]}', patches, f'{S}/v4k/final_new/{NAME4[k]}', f'{S}/splice/w4k_{k}')
