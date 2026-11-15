"""قياس توقيت مجموعة من الفيديو الأصلي فقط (بلا رسم): يكتب M في ملف .orig.log"""
import sys, json, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/regroup')
import regroup as G, sched as SC, partial as PT
S = G.S
cfg = json.load(open(sys.argv[1]))
hd, its = G.build(cfg['pages'], disk_r=cfg.get('disk_r', 38))
SL = json.load(open(f"{S}/slides/out/درس{cfg['lesson']}.json"))
refs = [PT.frame(cfg['video'], SL[i - 1]['t']) for i in cfg['refs']]
disks, bots = [], []
for it in its:
    ys, xs = np.nonzero(it.disk); disks.append((int(ys.mean()), int(xs.mean()), int(np.ptp(xs) / 2) + 4))
    ys2, _ = np.nonzero(it.lower & ~it.disk); bots.append(int(ys.max()) + 70)
for k, it in enumerate(its):
    if it.outline is not None and not it.outline.empty: bots[k] = int(it.outline.y1)
M = SC.measure(cfg['video'], cfg['A'], cfg['B'], refs, disks, bots, cfg.get('keep', False))
open(cfg['out'].replace('.mp4', '.orig.log'), 'w').write(json.dumps(M, ensure_ascii=False, default=float) + '\n')
print(json.dumps(M, ensure_ascii=False, default=float))
