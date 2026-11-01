"""إنزال «جَسَدِكَ) وهو اختيار ابن تيمية» إلى خط «هُوَ بَضْعَةٌ مِنْكَ أَوْ» (بعد إنزال «لا ينقض الوضوء»)؛ الأصل:
إنزال «لا ينقض الوضوء» إلى خط سطرها في القول الثاني (الدرس الأول) بإزاحة رأسية في كل إطار.

تُنقل بكسلات الكلمات الثلاث كما هي (بحالة كتابتها في كل إطار) dy نقطة إلى أسفل،
ويُعاد موضعها القديم إلى لون اللوح؛ وما تغطيه اليد لا يُمسّ.
الاستعمال: python3 shift_words.py in_seg.mp4 seg_start out.mp4
"""
import sys, subprocess, cv2, numpy as np

src, t0, dst = sys.argv[1], float(sys.argv[2]), sys.argv[3]
W, H, FPS = 1920, 1080, 30
DY = 9
X0, X1, Y0, Y1 = 110, 660, 900, 1062            # منطقة العمل (الكلمات وموضعها الجديد)
WIN = (779.0, 838.6)                            # من بدء الكتابة إلى انتهاء الانتقال
REF = np.array([228, 236, 240], np.float32)     # لون اللوح


def grab(t):
    r = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', src.replace('SEG', ''), '-frames:v', '1',
                        '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(H, W, 3).astype(np.float32)


def global_delta(fr):
    a = fr[20:60, 20:60].reshape(-1, 3); b = fr[600:640, 5:25].reshape(-1, 3)
    return np.median(np.vstack([a, b]), 0) - REF


# الحالة النهائية للمنطقة (الشريحة مكتملة بلا يد)
FIN = None
dec0 = subprocess.run(['ffmpeg', '-loglevel', 'error', '-ss', f'{830 - t0:.3f}', '-i', src, '-frames:v', '1', '-f', 'rawvideo',
                       '-pix_fmt', 'bgr24', '-'], capture_output=True).stdout
FIN = np.frombuffer(dec0, np.uint8).reshape(H, W, 3).astype(np.float32)[Y0:Y1, X0:X1]
LBG = np.median(FIN.reshape(-1, 3), 0)          # لون اللوح الفعلي في المنطقة
alpha = np.clip(np.abs(FIN - LBG).max(2) / 120.0, 0, 1)
ink = alpha > 0.1
n, lab, st, _ = cv2.connectedComponentsWithStats(ink.astype(np.uint8), 8)
ink = np.isin(lab, [i for i in range(1, n) if st[i, 4] >= 4])
words = np.zeros(alpha.shape, bool)
n2, lab2, st2, cen2 = cv2.connectedComponentsWithStats(ink.astype(np.uint8), 8)
for k in range(1, n2):                          # «جَسَدِكَ) وهو اختيار ابن تيمية»: يسار السطر الثاني
    cx, cy = cen2[k][0] + X0, cen2[k][1] + Y0
    if not (st2[k, 4] >= 4 and cy >= 928 and 140 <= cx <= 630): continue
    if cy < 950 and cx < 200: continue          # همزة «إنّما» وكسرتها تحت السطر الأول: ليستا من هذا السطر
    words |= lab2 == k
words = cv2.dilate(words.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
other = ink & ~words                            # حبر غيرها في المنطقة (لا يُمس)
REF = LBG
def sh(a):
    o = np.zeros_like(a)
    if DY > 0: o[DY:] = a[:-DY]
    else: o[:DY] = a[-DY:]
    return o
dest = sh(words)
w0 = np.zeros_like(words); w0[DY:] = (ink & words)[:-DY]
assert (w0 & other).sum() == 0, 'الموضع الجديد يلامس حبراً آخر'
v = FIN - REF                                   # لون الحبر النهائي نسبةً إلى اللوح

dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360',
                        '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
i = 0; touched = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    t = t0 + i / FPS
    if WIN[0] <= t <= WIN[1]:
        gd = global_delta(fr.astype(np.float32))
        reg = fr[Y0:Y1, X0:X1].astype(np.float32)
        bg = REF + gd
        # درجة ظهور الحبر النهائي (تخفت مع الانتقال)، وما لا يفسّره الحبر ولا اللوح فهو يد
        vv = (v * v).sum(2) + 1e-3
        lam = np.clip(((reg - bg) * v).sum(2) / vv, 0, 1.2)
        res = np.abs(reg - (bg + v * np.clip(lam, 0, 1)[..., None])).max(2)
        dark_pen = (reg.max(2) < 45) & (FIN.max(2) > 45)                     # القلم الأسود فوق اللوح
        Bc, Gc, Rc = reg[..., 0], reg[..., 1], reg[..., 2]
        cuff = reg.min(2) > bg.min() + 14                                   # الكمّ أبيض من اللوح
        skin = (Rc - Bc > 28) & (Rc > 140)
        raw = ((res > 34) | dark_pen | cuff | skin).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(raw, 8)
        big = np.isin(lab, [k for k in range(1, n) if st[k, 4] >= 250])     # اليد والقلم كتل كبيرة لا نقاط متفرقة
        if big.any():                                                        # اليد كتلة واحدة: تُسدّ فجواتها (ظلال الكمّ)
            solid = cv2.morphologyEx(big.astype(np.uint8), cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41)))
            from scipy import ndimage as ndi
            solid = ndi.binary_fill_holes(solid)
            hand = cv2.dilate(solid.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))) > 0
        else:
            hand = big
        out = reg.copy()
        if hand.any():
            # اليد حاضرة: يُنقل الحبر الداكن وحده؛ والقلم كتلة داكنة تمتد خارج الحروف فيُستثنى
            lum = reg.mean(2); blum = bg.mean()
            dark = (blum - lum) > 70
            n2, lab2, st2, _ = cv2.connectedComponentsWithStats(dark.astype(np.uint8), 8)
            wz = cv2.dilate(words.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            keep = [k for k in range(1, n2) if wz[lab2 == k].mean() > 0.9]
            ink_now = np.isin(lab2, keep)
            soft = cv2.dilate(ink_now.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
            soft &= ((blum - lum) > 8) & ((reg.max(2) - reg.min(2)) < 22)   # حواف الحروف الناعمة (رمادية لا لون جلد)
            bgl = (np.abs(reg - bg).max(2) < 9)                            # موضع لوحٍ خالٍ
            out[soft & words] = bg
            sh_soft = sh(soft)
            shifted = sh(reg)
            okd = sh_soft & (bgl | (soft & words))
            out[okd] = shifted[okd]
            fr[Y0:Y1, X0:X1] = np.clip(out, 0, 255).astype(np.uint8)
            touched += 1
            enc.stdin.write(fr.tobytes()); i += 1
            continue
        clear = words & ~hand
        out[clear] = bg
        shifted = sh(reg)
        src_hand = sh(hand)
        put = dest & ~hand & ~src_hand
        out[put] = shifted[put]
        out[dest & src_hand & ~hand] = bg
        fr[Y0:Y1, X0:X1] = np.clip(out, 0, 255).astype(np.uint8)
        touched += 1
    enc.stdin.write(fr.tobytes()); i += 1
enc.stdin.close(); enc.wait(); dec.wait()
print('frames', i, 'touched', touched)
