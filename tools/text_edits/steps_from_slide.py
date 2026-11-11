"""صور خطوات من شريحة مدمجة (1080): العنوان + عنصر واحد في كل خطوة، على لون اللوح المصمت، بلا أقراص."""
import cv2, numpy as np
BG = np.array([228, 236, 240], np.uint8)
HEAD = (180, 400, 340, 1580)          # y0, y1, x0, x1


def clean(img, y0, y1, x0, x1, out, thr=5):
    reg = img[y0:y1, x0:x1]
    d = np.abs(reg.astype(int) - BG.astype(int)).max(2) > thr
    d = cv2.dilate(d.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    o = out[y0:y1, x0:x1]; o[d] = reg[d]


def steps(slide, regions, disks, r=38):
    """regions: [(y0,y1,x0,x1)] لكل عنصر بترتيب رسمه؛ disks: [(cx,cy)] تُمحى."""
    outs, cums = [], []
    for k, rg in enumerate(regions):
        out = np.zeros_like(slide); out[:] = BG
        clean(slide, *HEAD, out)
        clean(slide, *rg, out)
        for (cx, cy) in disks: cv2.circle(out, (int(cx), int(cy)), r + 4, BG.tolist(), -1)
        outs.append(out)
    return outs


def cumulative(slide, regions, k):
    """الشريحة الأصلية بعناصرها حتى k (للقياس)، وما بعدها مصمت."""
    out = slide.copy()
    for j, (y0, y1, x0, x1) in enumerate(regions):
        if j > k: out[y0:y1, x0:x1] = BG
    return out
