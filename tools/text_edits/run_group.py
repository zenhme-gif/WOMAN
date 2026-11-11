"""python3 run_group.py cfg.json — إعادة رسم مجموعة بجدولة مقيسة."""
import sys, json, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/regroup')
import regroup as G, sched as SC
S = G.S
cfg = json.load(open(sys.argv[1]))
# العناصر الجديدة من الصفحات المعدّلة، والمراجع من شرائح الفيديو الأصلي
hd, its = G.build(cfg['pages'], disk_r=cfg.get('disk_r', 38))
import partial as PT
SL = json.load(open(f"{S}/slides/out/درس{cfg['lesson']}.json"))
refs = [PT.frame(cfg['video'], SL[i - 1]['t']) for i in cfg['refs']]          # إطار الفيديو نفسه (لون نصه كما هو)
disks, bots = [], []
for it in its:
    ys, xs = np.nonzero(it.disk); disks.append((int(ys.mean()), int(xs.mean()), int(np.ptp(xs) / 2) + 4))
    ys2, _ = np.nonzero(it.lower & ~it.disk); bots.append(int(ys.max()) + 70)
# أسفل إطار كل صندوق في الأصل: أول صف تحت القرص يبدأ بعده الشرح؛ تقريب: أسفل الإطار من عنصر الصفحة
for k, it in enumerate(its):
    if it.outline is not None and not it.outline.empty: bots[k] = int(it.outline.y1)
M = SC.measure(cfg['video'], cfg['A'], cfg['B'], refs, disks, bots, cfg.get('keep', False))
print(json.dumps(M, ensure_ascii=False, default=float))
tl = SC.plan(hd, its, cfg['A'], cfg['B'], M, cfg.get('keep', False), cfg['F'])
G.R.render(tl.ev, cfg['A'], cfg['B'], cfg['out'])
print('done', cfg['out'])
