"""تعديل نص شريحة نهائية (4K أو 1080): حذف مقطع من سطر وإعادة توسيطه، أو إحلال سطر مكان سطر.
لا يُمس إلا حبر السطر نفسه (مكوّنات مركزها في نطاق السطر)؛ وما سواه من الشريحة يبقى كما هو."""
import cv2, numpy as np


def line_comps(img, y0, y1, x0, x1, cy_lo, cy_hi):
    """ألفا حبر السطر (مكوّنات داكنة غير ملوّنة مركزها الرأسي بين cy_lo وcy_hi)، وخلفيته المرمّمة، ولون الحبر."""
    reg = img[y0:y1, x0:x1].astype(np.float32)
    L = reg.mean(2); sat = reg.max(2) - reg.min(2)
    dark = (L < 200) & (sat < 60)
    nl, lab, st, cen = cv2.connectedComponentsWithStats(dark.astype(np.uint8), 8)
    keep = np.zeros(L.shape, bool)
    for j in range(1, nl):
        if cy_lo <= cen[j][1] + y0 <= cy_hi: keep |= lab == j
    m = cv2.dilate(keep.astype(np.uint8), np.ones((7, 7), np.uint8))
    bg = cv2.inpaint(np.clip(reg, 0, 255).astype(np.uint8), m, 9, cv2.INPAINT_TELEA).astype(np.float32)
    Lb = bg.mean(2)
    core = keep & (L < 70)
    ink = np.median(reg[core].reshape(-1, 3), 0) if core.sum() > 50 else np.array([30, 30, 30], np.float32)
    a = np.clip((Lb - L) / np.maximum(Lb - ink.mean(), 1), 0, 1)
    a[~(cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)] = 0
    return a, bg, ink, m > 0


def split_by_cx(a, ranges, x0):
    """يقسم الحبر إلى طبقات بحسب مركز كل مكوّن الأفقي: ranges=[(lo,hi), ...] بإحداثيات الصورة."""
    nl, lab, st, cen = cv2.connectedComponentsWithStats((a > 0.03).astype(np.uint8), 8)
    out = [np.zeros(a.shape, np.float32) for _ in ranges]
    for j in range(1, nl):
        cx = cen[j][0] + x0; m = lab == j
        for k, (lo, hi) in enumerate(ranges):
            if lo <= cx < hi: out[k][m] = a[m]; break
    return out


def shift(a, dx, dy=0.0):
    h, w = a.shape
    return cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h), flags=cv2.INTER_LINEAR, borderValue=0)


def apply(img, box, layers, cy_rng):
    """box=(y0,y1,x0,x1)؛ layers: دالة (alpha, x0) → قائمة ألفا جديدة مُزاحة. يُرجع الصورة المعدّلة."""
    y0, y1, x0, x1 = box
    a, bg, ink, oldm = line_comps(img, y0, y1, x0, x1, *cy_rng)
    news = layers(a, x0)
    reg = img[y0:y1, x0:x1].astype(np.float32).copy()
    reg[oldm] = bg[oldm]                                        # محو السطر القديم وحده
    for s in news:
        reg = reg * (1 - s[..., None]) + ink * s[..., None]
    out = img.copy(); out[y0:y1, x0:x1] = np.clip(reg + 0.5, 0, 255).astype(np.uint8)
    return out, ink
