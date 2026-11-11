import sys, json, cv2, numpy as np
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
sys.path.insert(0, f'{S}/regroup')
import regroup as G, sched as SC, steps_from_slide as SF
V = '/home/user/WOMAN/lessons/lesson01-taharah-wudu-ghusl.mp4'
A, F, B = 675.3, 711.8667, 712.4333
REG = [(395, 640, 1150, 1660), (395, 725, 100, 960), (730, 1000, 1050, 1680), (730, 1015, 100, 960)]
DISKS = [(1398, 436), (528, 436), (1398, 771), (528, 771)]
new = cv2.imread(f'{S}/slides_edit/درس1/16.png')
import partial as PT
old = PT.frame(V, 711.6)                     # الإطار الأخير قبل الانتقال (لون النص كما في الفيديو)
st = SF.steps(new, REG, DISKS)
for k, s in enumerate(st): cv2.imwrite(f'{S}/regroup/kh_step{k+1}.png', s)
G.R.Item.OUT_MIN = (50, 50); G.R.Item.BODY_PAD = 8
hd, its = G.build(None, step_imgs=st, disk_r=38)
for it in its:                                   # شظايا حواف الإطار ليست نصاً
    it.boxtext = [s for s in it.boxtext if (s.a > 0.3).sum() > 400]
refs = [SF.cumulative(old, REG, k) for k in range(4)]
disks, bots = [], []
for it in its:
    ys, xs = np.nonzero(it.disk); disks.append((int(ys.mean()), int(xs.mean()), int(np.ptp(xs) / 2) + 4))
    bots.append(int(it.outline.y1))
print('disks', disks, 'bots', bots, 'lines', [len(it.lines) for it in its], 'boxtext', [len(it.boxtext) for it in its], flush=True)
if len(sys.argv) > 1 and sys.argv[1] == 'dry': sys.exit()
if 'reuse' in sys.argv[1:]:
    M = [json.loads(l) for l in open(f'{S}/regroup/l1_e3.log') if l.startswith('{')][-1]
else:
    M = SC.measure(V, A, B, refs, disks, bots, True)
    print(json.dumps(M, ensure_ascii=False, default=float), flush=True)
tl = SC.plan(hd, its, A, B, M, True, F)
G.R.render(tl.ev, A, B, f'{S}/regroup/l1_e3.mp4')
print('done')
