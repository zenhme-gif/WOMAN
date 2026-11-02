"""تركيب الأجزاء المصلحة: يُقسَم كل جزء قديم عند الإطارات المفتاحية، وتُستبدل قطع الانتقالات، ويُتحقق من عدد الإطارات."""
import json, subprocess, os, glob, shutil
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
plan = json.load(open(f'{S}/v4k/fixplan.json'))
cnt = lambda p: int(subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
for name, p in plan.items():
    if not p['ranges']: continue
    ch = f'{S}/v4k/chunks/l{name}.mp4'; tmp = f'{S}/v4k/fix/split_{name}'
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    cuts = sorted({x for r in p['ranges'] for x in r if 0 < x < p['n']})
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', ch, '-map', '0:v', '-c', 'copy', '-f', 'segment', '-segment_frames', ','.join(map(str, cuts)),
                    '-reset_timestamps', '1', '-segment_format', 'mp4', f'{tmp}/s%03d.mp4'], check=True)
    bounds = [0] + cuts + [p['n']]
    segs = sorted(glob.glob(f'{tmp}/s*.mp4'))
    assert len(segs) == len(bounds) - 1, (name, len(segs), len(bounds))
    files = []
    for i, sg in enumerate(segs):
        a, b = bounds[i], bounds[i + 1]
        n = cnt(sg); assert n == b - a, (name, i, n, b - a)
        rep = [r for r in p['ranges'] if r[0] == a]
        if rep:
            fx = f'{S}/v4k/fix/l{name}_{a:05d}.mp4'; assert cnt(fx) == b - a, (name, a, cnt(fx), b - a); files.append(fx)
        else: files.append(sg)
    lst = f'{tmp}/list.txt'; open(lst, 'w').write(''.join(f"file '{f}'\n" for f in files))
    out = f'{S}/v4k/chunks/l{name}.fixed.mp4'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', out], check=True)
    assert cnt(out) == p['n'], (name, cnt(out), p['n'])
    os.replace(ch, f'{S}/v4k/chunks/old_l{name}.mp4.bak'); os.replace(out, ch)
    print(name, 'fixed', len(p['ranges']), 'pieces; frames', p['n'], flush=True)
