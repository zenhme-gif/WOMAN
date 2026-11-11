import numpy as np, bt
def joint(n, xa, xb, base, up=130, down=70):
    """أنحف عمود بين xa وxb (موضع الوصلة بين حرفين): أقل حبر في العمود."""
    a = bt.alpha(bt.page(n)[int(base - up):int(base + down), xa:xb])
    col = (a > 0.4).sum(0)
    return xa + int(np.argmin(col)), col.min()
