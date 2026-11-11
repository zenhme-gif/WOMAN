"""الدرس الأول، خريطة التنجية: إعادة رسم «القول الثاني» بالنص الجديد من 13:00.2 إلى نهاية المجموعة."""
import sys, json, cv2, numpy as np
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
sys.path.insert(0, f'{S}/regroup')
import partial as PT, steps_from_slide as SF
R = PT.R
V = '/home/user/WOMAN/lessons/lesson01-taharah-wudu-ghusl.mp4'
Ts, T_free, F_, B = 780.2, 790.5, 837.6333, 838.5667
W0, W1 = 780.5, 790.2                 # كتابة الشرح القديم في الأصل
C0 = 790.9                            # بدء التلوين في الأصل
board, _ = PT.clean_board(V, T_free, (875, 1075, 100, 975), (882, 1020))
F = PT.frame(V, Ts)
tip, e = PT.find_tip(F, board); print('tip', tip, 'err', round(e, 2))
board = PT.board_at(F, tip, board)
new = cv2.imread(f'{S}/slides_edit/درس1/18.png')
alpha = np.load(f'{S}/txt/e4_alpha1080.npy')
ink = np.median(new[(alpha > 0.9)].reshape(-1, 3), 0).astype(np.float32); print('ink', ink)
col = np.zeros((1080, 1920, 3), np.float32) + ink
lines = [R.wipe_rtl(m, col) for m in R.split_lines(alpha)]
print('lines', [(l.y0, l.y1, l.x0, l.x1) for l in lines])
# التلوين: اللافتة من الشريحة، والأقراص الثلاثة
st = np.zeros_like(new); st[:] = SF.BG; SF.clean(new, *SF.HEAD, st)
bg = np.median(st[:40, :40].reshape(-1, 3), 0).astype(np.float32)
hd = R.Header(st, bg)
disks = sorted(PT.disks_of(new), key=lambda d: d[0])                # كالأصل: الأيسر ثم العلوي ثم الأيمن
print('disks', disks)
fills = [PT.disk_fill(new, cx, cy, r) for cx, cy, r in disks]
# الجدول
tl = R.Timeline(Ts); tl.hand = 'pen'; tl.pos = tip.copy()
wid = [l.x1 - l.x0 for l in lines]; tot = W1 - W0 - 0.25 * (len(lines) - 1)
t = W0
for l, w in zip(lines, wid):
    d = tot * w / sum(wid)
    tl.draw(l, d, earliest=t, gap=0.2); t = tl.t + 0.25
cs = [(hd.fill, 2.8, 0.3)] + [(f, 0.6, 0.15) for f in fills]
R.seq(tl, cs, 2.6, earliest=C0, minf=0.2, maxf=0.8)
tl.leave()
print('drawing ends', round(tl.t, 2))
tl.ev.append(('fade', F_, B))
if len(sys.argv) > 1 and sys.argv[1] == 'dry':
    # الإطار الأول مقابل الأصل
    import subprocess
    R.render(tl.ev, Ts, Ts + 2 / 30, f'{S}/regroup/tj_test.mp4', base=board)
    sys.exit()
R.render(tl.ev, Ts, B, f'{S}/regroup/l1_e4.mp4', base=board)
print('done')
