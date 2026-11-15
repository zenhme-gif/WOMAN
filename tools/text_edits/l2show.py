"""عرض مناطق من الصفحات 4K بمسطرة إحداثيات، مكدّسة في صورة واحدة: python3 l2show.py out.png n:x0:x1:base ..."""
import sys, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/txt')
import bt
out = sys.argv[1]; ims = []
for spec in sys.argv[2:]:
    n, x0, x1, b = map(float, spec.split(':')); n, x0, x1 = int(n), int(x0), int(x1)
    y0, y1 = int(b - 150), int(b + 70)
    a = bt.alpha(bt.page(n)[y0:y1, x0:x1])
    im = cv2.cvtColor((255 - a * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
    sc = 1.0
    for x in range(x0 - x0 % 10, x1, 10):
        if x < x0: continue
        big = x % 50 == 0
        cv2.line(im, (x - x0, 0), (x - x0, 14 if big else 6), (0, 0, 255), 1)
        if big: cv2.putText(im, str(x), (x - x0 + 2, 26), 0, 0.42, (0, 0, 255), 1)
    yb = int(b - y0); cv2.line(im, (0, yb), (im.shape[1], yb), (255, 160, 0), 1)
    cv2.putText(im, f'p{n} b{int(b)}', (4, im.shape[0] - 6), 0, 0.5, (0, 140, 0), 1)
    ims.append(im)
Wd = max(i.shape[1] for i in ims)
ims = [cv2.copyMakeBorder(i, 0, 4, 0, Wd - i.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for i in ims]
cv2.imwrite(out, np.vstack(ims))
