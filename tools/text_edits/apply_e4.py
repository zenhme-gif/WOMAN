import sys, pickle, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt, slide_edit as SE
S = bt.S
D = pickle.load(open(f'{S}/txt/e4.pkl', 'rb'))
s = 0.674; CX = 1058.0
lines = []
for k in ('L1', 'L2', 'L3'):
    a, b = D[k]
    r = cv2.resize(a, (round(a.shape[1] * s), round(a.shape[0] * s)), interpolation=cv2.INTER_AREA)
    lines.append((np.clip(r, 0, 1).astype(np.float32), b * s))

def layout(base1, pitch, Hh=2160, Ww=3840):
    out = []
    for i, (a, b) in enumerate(lines):
        y0 = base1 + i * pitch - b; x0 = CX - a.shape[1] / 2
        out.append((a, x0, y0))
    return out

def canvas_of(L, Hh=2160, Ww=3840):
    cs = []
    for a, x0, y0 in L:
        c = np.zeros((Hh, Ww), np.float32)
        M = np.float32([[1, 0, x0], [0, 1, y0]])
        cs.append(cv2.warpAffine(a, M, (Ww, Hh), flags=cv2.INTER_LINEAR))
    return cs

base1 = 1850
for pitch in range(112, 127, 2):
    cs = canvas_of(layout(base1, pitch))
    k = np.ones((5, 5), np.uint8)
    ov = [int(((cv2.dilate((cs[i] > 0.2).astype(np.uint8), k) > 0) & (cs[i + 1] > 0.2)).sum()) for i in range(2)]
    ys = np.nonzero(cs[2].max(1) > 0.2)[0]
    print('pitch', pitch, 'overlap', ov, 'L3 bottom', ys.max(), 'L1 top', np.nonzero(cs[0].max(1) > 0.2)[0].min())

if __name__ == '__main__':
    PITCH = 120
    cs = canvas_of(layout(base1, PITCH))
    new4k = np.maximum.reduce(cs)
    np.save(f'{S}/txt/e4_alpha4k.npy', new4k)
    # 4K
    img = cv2.imread(f'{S}/hr/out/درس1/18.png')
    box = (1750, 2150, 200, 1950)
    out, ink = SE.apply(img, box, lambda a, x0: [new4k[box[0]:box[1], box[2]:box[3]]], (1765, 2040))
    cv2.imwrite(f'{S}/hr/out_edit/درس1/18.png', out); print('4K ink', ink)
    # 1080
    sm = cv2.resize(new4k, (1920, 1080), interpolation=cv2.INTER_AREA)
    np.save(f'{S}/txt/e4_alpha1080.npy', sm)
    img2 = cv2.imread(f'{S}/slides/out/درس1/18.png')
    b2 = (875, 1075, 100, 975)
    out2, ink2 = SE.apply(img2, b2, lambda a, x0: [sm[b2[0]:b2[1], b2[2]:b2[3]]], (882, 1020))
    cv2.imwrite(f'{S}/slides_edit/درس1/18.png', out2); print('1080 ink', ink2)
    cv2.imwrite(f'{S}/txt/e4_4k.png', cv2.resize(np.vstack([img[1650:2160, 0:2000], out[1650:2160, 0:2000]]), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
    cv2.imwrite(f'{S}/txt/e4_1080.png', np.vstack([img2[820:1080, 0:1000], out2[820:1080, 0:1000]]))
