"""خطة إصلاح الانتقالات في الأجزاء التي أُخرجت قبل الإصلاح: لكل انتقال تُعاد مجموعة الإطارات من الإطار المفتاحي
الذي قبله إلى الذي بعده فقط، ثم تُوضع مكانها."""
import json, subprocess, glob
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
SRC = {1: '/home/user/WOMAN/lessons/lesson01-taharah-wudu-ghusl.mp4', 2: '/home/user/WOMAN/lessons/lesson02-taharah-hayd-nifas.mp4', 3: f'{S}/slides/l3.mp4'}
OLD = {1: range(6), 2: range(6), 3: range(2)}
jobs = []; plan = {}
for k, cs in OLD.items():
    fades = json.load(open(f'{S}/v4k/fades{k}.json'))
    for c in cs:
        ch = f'{S}/v4k/chunks/l{k}_{c:02d}.mp4'; n0 = c * 6000
        nfr = int(subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', ch], capture_output=True, text=True).stdout)
        kf = [int(float(x.split(',')[0]) * 30 + 0.5) for x in subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-skip_frame', 'nokey', '-show_entries', 'frame=pts_time', '-of', 'csv=p=0', ch], capture_output=True, text=True).stdout.split()]
        rng = []
        for a, b in fades:
            a, b = a - n0, b - n0
            if b < 0 or a >= nfr: continue
            a, b = max(a, 0), min(b, nfr - 1)
            ka = max(x for x in kf if x <= a); kb = min([x for x in kf if x > b + 1] + [nfr])
            if rng and ka <= rng[-1][1]: rng[-1][1] = max(rng[-1][1], kb)
            else: rng.append([ka, kb])
        plan[f'{k}_{c:02d}'] = dict(n=nfr, kf=kf, ranges=rng)
        for ka, kb in rng:
            jobs.append(f'{k} {SRC[k]} {n0 + ka} {n0 + kb} {S}/v4k/fix/l{k}_{c:02d}_{ka:05d}.mp4')
json.dump(plan, open(f'{S}/v4k/fixplan.json', 'w'))
jobs.append(f'3 {SRC[3]} 12000 18000 {S}/v4k/chunks/l3_02.mp4')       # جزء أُوقف قبل اكتماله
open(f'{S}/v4k/jobs_fix.txt', 'w').write('\n'.join(jobs) + '\n')
print(len(jobs), 'jobs', sum(b - a for p in plan.values() for a, b in p['ranges']), 'frames to redo (+6000 for l3_02)')
