"""محو حرف المقدمة المبكر في نسخ 1080 للدروس 2 و3 و4: python3 mark_lessons.py K"""
import sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/splice')
import splice as SP, intro_mark as IM
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
k = int(sys.argv[1])
src = {2: '/home/user/WOMAN/lessons/lesson02-taharah-hayd-nifas.mp4', 3: f'{S}/splice/lesson03_new.mp4', 4: f'{S}/splice/lesson04_new.mp4'}[k]
t0, r0, r1 = IM.LESSONS[k]
im = IM.IntroMark(src, t0, r0, r1)
out = f'{S}/splice/lesson{k:02d}_new.mp4'; tmp = out + '.mark.mp4'
SP.run(src, [(im.n0 / 30, im.n1 / 30, im.get)], tmp, f'{S}/splice/wm{k}')
os.replace(tmp, out); print('ok', k, 'mask px', int(im.M.sum()))
