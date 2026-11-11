"""مقارنة إطارات المقطع المعاد رسمه بالأصل: python3 cmp.py cfg.json out.jpg t1 t2 ..."""
import sys, json, subprocess, cv2, numpy as np
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
def fr(v, t):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', v, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(1080, 1920, 3).copy()
rows = []
for t in ts:
    a = cv2.resize(fr(cfg['video'], t), (768, 432)); b = cv2.resize(fr(cfg['out'], t - cfg['A']), (768, 432))
    cv2.putText(a, f'orig {t:.1f}', (10, 425), 0, 0.6, (0, 0, 255), 2); cv2.putText(b, f'new {t:.1f}', (10, 425), 0, 0.6, (0, 0, 255), 2)
    rows.append(np.hstack([a, np.full((432, 6, 3), 255, np.uint8), b]))
cv2.imwrite(out, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 85])
