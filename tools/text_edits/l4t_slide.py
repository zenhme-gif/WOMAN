"""شريحة 1080 الجديدة 01 للدرس الرابع: يُمحى نص المربع الأول (ألفا مقيسة من الشريحة) ويوضع الجديد."""
import cv2, numpy as np
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
REG = (440, 522, 1450, 1660)            # y0, y1, x0, x1: منطقة نص المربع الأول (داخل الإطار)


def old_alpha(img):
    """ألفا النص القديم ولونه ولون الخلفية، من صورة 1080 (شريحة أو إطار نظيف)."""
    y0, y1, x0, x1 = REG
    r = img[y0:y1, x0:x1].astype(np.float32)
    L = r.mean(2)
    bg = np.median(r[L > np.percentile(L, 60)].reshape(-1, 3), 0)
    ink = np.median(r[L < np.percentile(L, 3)].reshape(-1, 3), 0)
    a = np.clip((bg.mean() - L) / (bg.mean() - ink.mean()), -0.5, 1)      # موقَّعة: تشمل هالة الضغط الفاتحة
    near = cv2.dilate((a > 0.12).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    far = ~(cv2.dilate(near.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0)
    bg = np.median(r[far].reshape(-1, 3), 0)                                # خلفية المربع الفعلية (بعيداً عن النص)
    a = np.clip((bg.mean() - L) / (bg.mean() - ink.mean()), -0.5, 1)
    a[~near] = 0
    A = np.zeros(img.shape[:2], np.float32); A[y0:y1, x0:x1] = a
    return A, bg, ink


if __name__ == '__main__':
    s = cv2.imread(f'{S}/slides/out_orig/درس4/01.png')
    A_old, bg, ink = old_alpha(s)
    A_new = np.load(f'{S}/txt/l4t_a1.npy')
    print('bg', bg, 'ink', ink, 'old ink sum', A_old.sum(), 'new ink sum', A_new.sum())
    out = s.astype(np.float32) + (A_new - A_old)[..., None] * (ink - bg)
    out = np.clip(out + 0.5, 0, 255).astype(np.uint8)
    cv2.imwrite(f'{S}/slides_edit/درس4/01.png', out)
    y0, y1, x0, x1 = REG
    cv2.imwrite(f'{S}/txt/l4t_slide.png', cv2.resize(np.vstack([s[400:560, 1360:1760], out[400:560, 1360:1760]]), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST))
