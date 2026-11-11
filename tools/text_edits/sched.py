"""جدولة دقيقة لمجموعة مُعادة الرسم: أزمنة كل عنصر مقيسة من الفيديو الأصلي.
- العنوان: من بدء ظهوره إلى ظهور حلقة القرص الأول.
- كل صندوق: إطاره ونصه من ظهور حلقته إلى بدء أسطر الشرح؛ والأسطر من بدئها إلى اكتمالها في الأصل.
- المسح بين الصناديق، والتلوين، والانتقال: في أزمنة الأصل."""
import sys, subprocess, cv2, numpy as np
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
sys.path.insert(0, f'{S}/r2')
import render2 as R
W, H, FPS = 1920, 1080, 30


def stream(video, A, B):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{A:.4f}', '-i', video, '-t', f'{B - A:.4f}', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)
    p.wait()


def split_rows(prof, line_h=70):
    """أسطر النص: تُفصل أولاً بالصفوف الفارغة؛ وما طال من الكتل (أسطر متلامسة) يُقسم عند أخف صف بين خطوط القاعدة."""
    rows = prof > 0; runs = []; y = 0
    while y < len(rows):
        if rows[y]:
            s0 = y
            while y < len(rows) and rows[y]: y += 1
            runs.append([s0, y])
        y += 1
    big = [r for r in runs if r[1] - r[0] >= 14]
    if not big: return []
    for r in runs:                                      # الحركات المنفصلة تُضم إلى أقرب سطر
        if r in big: continue
        c = (r[0] + r[1]) / 2
        k = int(np.argmin([abs(c - (b[0] + b[1]) / 2) for b in big]))
        big[k] = [min(big[k][0], r[0]), max(big[k][1], r[1])]
    out = []
    p = np.convolve(prof.astype(float), np.ones(5) / 5, 'same')
    for a, b in sorted(big):
        if b - a <= line_h * 1.3: out.append((a, b)); continue
        seg = p[a:b]; peaks = []
        for y in np.argsort(-seg):
            if seg[y] < 0.1 * seg.max(): break
            if all(abs(y - q) >= 44 for q in peaks): peaks.append(int(y))
        peaks.sort()
        cuts = [a] + [a + int(u + np.argmin(seg[u:v])) for u, v in zip(peaks[:-1], peaks[1:])] + [b]
        out += [(cuts[i], cuts[i + 1]) for i in range(len(cuts) - 1)]
    # الحدود بين الأسطر في منتصف الفراغ
    res = []
    for i, (a, b) in enumerate(out):
        a2 = (out[i - 1][1] + a) // 2 if i else a
        b2 = (b + out[i + 1][0]) // 2 if i + 1 < len(out) else b
        res.append((a2, b2))
    return res


def measure(video, A, B, refs, disks, box_bottoms, keep):
    """refs: صورة كل صندوق مكتملاً (1080) من الفيديو الأصلي؛ disks: (cy,cx,r)."""
    PL = R.PLATE.astype(np.int16)
    masks = []
    for k, ref in enumerate(refs):
        d = (ref.max(2) < 110) & ((ref.max(2).astype(int) - ref.min(2)) < 40)
        d[:box_bottoms[k] + 8] = False
        d[1030:] = False; d[:, :150] = False; d[:, 1770:] = False      # زخارف اللوح أسفل الإطار وطرفيه
        if keep and k: d &= ~((refs[k - 1].max(2) < 110))
        masks.append(d)
    bands = [split_rows(d.sum(1)) for d in masks]
    lc = [[[] for _ in b] for b in bands]
    tc, rc, bc, red = [], [[] for _ in refs], [[] for _ in refs], []
    for f in stream(video, A, B):
        fi = f.astype(np.int16)
        tc.append(int((np.abs(fi[150:430, 300:1620] - PL[150:430, 300:1620]).max(2) > 40).sum()))
        sub = f[60:440, 200:1720].astype(np.int16)
        red.append(int(((sub[..., 2] > 180) & (sub[..., 1] < 130) & (sub[..., 0] < 140)).sum()))
        for k, (cy, cx, r) in enumerate(disks):
            s = fi[cy - r:cy + r, cx - r:cx + r]
            rc[k].append(int(((s[..., 2] > 200) & (s[..., 1] > 180) & (s[..., 0] < 135) & (s[..., 2] - s[..., 0] > 95)).sum()))
            m = masks[k]
            ok = np.zeros(m.shape, bool); ok[m] = np.abs(fi[m] - refs[k][m].astype(np.int16)).max(1) < 35
            bc[k].append(int(ok.sum()))
            for j, (y0, y1) in enumerate(bands[k]): lc[k][j].append(int(ok[y0:y1].sum()))
    tc, red = np.array(tc), np.array(red)
    T = lambda i: A + i / FPS
    out = dict(title=T(int(np.argmax(tc > 150))), items=[])
    i_prev = 0
    for k in range(len(refs)):
        c = np.array(rc[k]); on = np.nonzero(c[i_prev:] > 25)[0]
        i_ring = i_prev + on[0]
        b = np.array(bc[k]); mx = b[i_ring:].max()
        if mx < 60:                                   # صندوق بلا شرح: تُقدَّر نهايته لاحقاً
            i_b0 = i_b1 = None
        else:
            i_b0 = i_ring + int(np.argmax(b[i_ring:] > 0.03 * mx))
            i_b1 = i_ring + int(np.argmax(b[i_ring:] > 0.97 * mx))
        lowrun = np.convolve((c[i_ring:] <= 5).astype(int), np.ones(10, int), 'valid')
        off = np.nonzero(lowrun == 10)[0]
        i_clear = i_ring + off[0] if len(off) else None
        lines_t, bnds = [], []
        for j in range(len(bands[k])):
            L = np.array(lc[k][j]); lm = L[i_ring:].max()
            if lm < 30: continue
            run = np.convolve((L[i_ring:] > 0.12 * lm).astype(int), np.ones(8, int), 'valid')   # حبر ثابت ربع ثانية (لا رأس القلم العابر)
            i0 = i_ring + (int(np.argmax(run == 8)) if (run == 8).any() else int(np.argmax(L[i_ring:] > 0.04 * lm)))
            # القلم يمر فوق السطر التالي أثناء كتابة سابقه: لا يبدأ سطر قبل مضي نصف المدة الطبيعية لكتابة سابقه
            if lines_t: i0 = max(i0, prev_i0 + int(0.5 * prev_w / 165.0 * FPS))
            cols = np.nonzero(masks[k][bands[k][j][0]:bands[k][j][1]].any(0))[0]
            prev_i0, prev_w = i0, (int(cols.max() - cols.min()) if len(cols) else 0)
            lines_t.append((T(i0), T(i_ring + int(np.argmax(L[i_ring:] > 0.96 * lm)))))
            bnds.append(bands[k][j])
        out['items'].append(dict(lines=lines_t, bands=bnds, ring=T(i_ring), body0=None if i_b0 is None else T(i_b0), body1=None if i_b1 is None else T(i_b1),
                                 clear=T(i_clear) if (i_clear is not None and not keep and k + 1 < len(refs)) else None))
        i_prev = (i_clear if i_clear is not None and not keep else i_ring) + 1
    for k, m in enumerate(out['items']):              # بلا شرح: ينتهي الصندوق قبل الحلقة التالية
        if m['body0'] is None:
            nxt = out['items'][k + 1]['ring'] if k + 1 < len(out['items']) else None
            m['body0'] = m['body1'] = (nxt - 0.4) if nxt else m['ring'] + 4.0
            m['nobody'] = True
    i_last = int((out['items'][-1]['body1'] - A) * FPS)
    base_red = int(np.median(red[max(0, i_last - 30):i_last + 1])); out['color'] = T(i_last + int(np.argmax(red[i_last:] > base_red + 5000)))
    return out


def resplit(strokes, bands):
    """يجمع أسطر الشرح الجديدة ثم يقسمها على حدود أسطر الأصل (منتصف الفراغ بين كل سطرين)."""
    A = np.zeros((H, W), np.float32); C = np.zeros((H, W, 3), np.float32)
    for s in strokes:
        sl = (slice(s.y0, s.y1), slice(s.x0, s.x1))
        m = s.a > A[sl]; A[sl] = np.maximum(A[sl], s.a); C[sl][m] = s.c[m]
    cuts = [-1] + [(bands[j][1] + bands[j + 1][0]) // 2 for j in range(len(bands) - 1)] + [H + 1]
    out = []
    for j in range(len(bands)):
        a = A.copy(); a[:max(0, cuts[j])] = 0; a[min(H, cuts[j + 1]):] = 0
        st = R.wipe_rtl(a, C)
        out.append(None if (st is None or st.empty) else st)
    return out


def plan(header, items, A, B, M, keep, fade_start):
    tl = R.Timeline(A)
    it0 = M['items'][0]
    hs = [(header.brackets[0] if header.brackets else None, 0.5, 0.15), (header.banner_loop, 2.4, 0.15),
          (header.brackets[1] if len(header.brackets) > 1 else None, 0.4, 0.15), (header.title, 4.2 if header.two_lines else 3.0, 0.15)]
    R.seq(tl, hs, it0['ring'] - 0.35 - M['title'], earliest=M['title'], minf=0.15, maxf=1.0)
    for k, (it, m) in enumerate(zip(items, M['items'])):
        if k and not keep and M['items'][k - 1]['clear'] is not None:
            tl.clear(items[k - 1].lower, M['items'][k - 1]['clear'])
        sub = [(it.ring, 0.6, 0.1), (it.digit, 0.3, 0.08), (it.outline, 2.0, 0.12)] + \
              [(s, max(0.8, R.text_nat(s)), 0.08) for s in it.boxtext if s] + [(it.hl, 0.4, 0.08), (it.arrow, 0.3, 0.08)]
        R.seq(tl, sub, m['body0'] - 0.05 - max(tl.t, m['ring']), earliest=m['ring'], minf=0.15, maxf=1.0)
        ls = [s for s in it.lines if s and not s.empty]
        lt = m.get('lines') or []
        if ls and lt:                                 # أسطر الجديد على حدود أسطر الأصل، وكل سطر يبدأ حين بدأ في الأصل
            ls = resplit(ls, m['bands'])
            win = [(a0, min(a1, lt[j + 1][0] - 0.3) if j + 1 < len(lt) else min(a1, m['body1'])) for j, (a0, a1) in enumerate(lt)]
            nat = [R.text_nat(x) if x is not None else 0 for x in ls]
            if any(n and (e - a) < n / 1.8 for (a, e), n in zip(win, nat)) and sum(nat):
                # بدايات مقيسة تضغط سطراً ضغطاً شديداً: تُوزَّع نافذة الكتابة كلها بحسب أطوال الأسطر
                s0, e1 = win[0][0], win[-1][1]; T = max(e1 - s0 - 0.25 * (len(ls) - 1), 0.6 * len(ls)); t = s0; win = []
                for n in nat:
                    d = T * n / sum(nat); win.append((t, t + d)); t += d + 0.25
            for st_, (a0, end) in zip(ls, win):
                start = max(a0, tl.t + 0.2)
                if st_ is not None: tl.draw(st_, max(0.6, end - start), earliest=a0, gap=0.2)
        else:
            if ls: print('  أسطر الأصل', len(lt), 'والجديد', len(ls), '— توزيع على مدة الشرح')
            body = [(s, max(1.0, R.text_nat(s)), 0.2) for s in ls]
            R.seq(tl, body, m['body1'] - max(tl.t, m['body0']), earliest=m['body0'], minf=0.15, maxf=1.6)
    shown = items if keep else items[-1:]
    cs = [(header.fill, 2.8, 0.3)] + [(it.disk_fill, 0.6, 0.15) for it in shown]
    R.seq(tl, cs, fade_start - 1.1 - M['color'], earliest=M['color'] - 0.4, minf=0.15, maxf=1.0)
    tl.leave()
    f0 = max(tl.t, fade_start)
    if f0 > fade_start + 0.25: print('  تنبيه: تأخر الرسم عن بدء انتقال الأصل', round(f0 - fade_start, 2))
    tl.ev.append(('fade', min(f0, B - 0.35), B)); tl.t = B
    return tl
