import sys, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt
def lines(n, y0=1330, y1=2150):
    a = bt.alpha(bt.page(n)[y0:y1, 300:3540]) > 0.4
    prof = a.sum(1)
    rows = np.nonzero(prof > 0)[0]
    runs = []; s = rows[0]; p = rows[0]
    for r in rows[1:]:
        if r - p > 6: runs.append((s + y0, p + y0)); s = r
        p = r
    runs.append((s + y0, p + y0))
    out = []
    for (u, v) in runs:
        if v - u < 40: continue
        b = bt.line_base(n, u, v + 5)
        out.append((u, v, b))
    return out
if __name__ == '__main__':
    for n in map(int, sys.argv[1:]):
        L = lines(n)
        print(n, [(u, v, b) for u, v, b in L])
        for u, v, b in L:
            if b: print('   base', b, bt.spans(n, int(b - 130), int(b + 60), 400, 3500, gap=22))
