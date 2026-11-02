"""تكبير الرسوم المسطحة مرتين بحواف حادة ناعمة: كل نقطة تُعاد بين أدنى وأعلى قيمة في جوارها الأصلي
بانتقال أضيق، فلا تُختلق أشكال جديدة ولا يظهر تدرّج مموَّه."""
import cv2, numpy as np


def sharp_up(img, k=2.4):
    f = img.astype(np.float32)
    U = cv2.resize(f, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    ker = np.ones((3, 3), np.uint8)
    lo = cv2.resize(cv2.erode(f, ker), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    hi = cv2.resize(cv2.dilate(f, ker), None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
    rng = hi - lo
    t = np.clip((U - lo) / np.maximum(rng, 1e-3), 0, 1)
    t2 = np.clip((t - 0.5) * k + 0.5, 0, 1)
    t2 = t2 * t2 * (3 - 2 * t2)
    out = np.where(rng > 6, lo + rng * t2, U)
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)
