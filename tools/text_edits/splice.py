"""وصل مقاطع معاد رسمها في درس منتج دون إعادة ترميز بقيته.
يُقطع الدرس عند الإطارات المفتاحية المحيطة بكل رقعة، ويُعاد ترميز تلك القطع وحدها بعد إحلال إطاراتها،
ثم يُجمع الكل بالنسخ ويُضم الصوت الأصلي. يُتحقق من عدد الإطارات والمدة.
الرقعة: (n0, n1, get) حيث get(n, frame_orig) يعيد الإطار البديل للإطار رقم n (أو None للإبقاء)."""
import subprocess, os, numpy as np, json
W, H, FPS = 1920, 1080, 30
ENC = ['-sws_flags', 'accurate_rnd+full_chroma_int+bitexact', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
       '-pix_fmt', 'yuv420p', '-video_track_timescale', '15360']


def keyframes(src):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'packet=pts_time,flags', '-of', 'csv=p=0', src],
                         capture_output=True, text=True).stdout
    ks = []
    for l in out.splitlines():
        p = l.split(',')
        if len(p) >= 2 and 'K' in p[1]: ks.append(float(p[0]))
    return sorted(ks)


def nframes(p):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v', '-count_packets', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', p],
                         capture_output=True, text=True).stdout
    return int(out.strip())


class Clip:
    """إطارات مقطع معاد رسمه يبدأ عند الإطار n_start من الدرس."""
    def __init__(self, path, t_start):
        self.path, self.n0 = path, int(round(t_start * FPS)); self.p = None; self.i = None

    def get(self, n, f):
        k = n - self.n0
        if self.p is None or k < self.i:
            if self.p: self.p.kill()
            self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{k / FPS:.4f}', '-i', self.path, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
            self.i = k
        while self.i <= k:
            b = self.p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: return None
            fr = np.frombuffer(b, np.uint8).reshape(H, W, 3); self.i += 1
        return fr


def run(src, patches, out, work):
    os.makedirs(work, exist_ok=True)
    ks = keyframes(src); kn = [int(round(k * FPS)) for k in ks]
    total = nframes(src)
    # حدود القطع: أقرب إطار مفتاحي قبل الرقعة وبعدها
    spans = []
    for n0, n1, _ in patches:
        a = max([k for k in kn if k <= n0]); b = min([k for k in kn if k >= n1] + [total])
        spans.append([a, b])
    spans.sort(); merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], b)
        else: merged.append([a, b])
    cuts = sorted(set([x for ab in merged for x in ab if 0 < x < total]))
    print('spans', [(a / FPS, b / FPS) for a, b in merged], flush=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-map', '0:v', '-c', 'copy', '-f', 'segment',
                    '-segment_times', ','.join(f'{c / FPS - 0.005:.4f}' for c in cuts), '-reset_timestamps', '1', '-segment_format', 'mp4',
                    f'{work}/s%03d.mp4'], check=True)
    bounds = [0] + cuts + [total]
    segs = []
    for i in range(len(bounds) - 1):
        p = f'{work}/s{i:03d}.mp4'; nf = nframes(p)
        assert nf == bounds[i + 1] - bounds[i], (p, nf, bounds[i], bounds[i + 1])
        a, b = bounds[i], bounds[i + 1]
        mine = [(n0, n1, g) for n0, n1, g in patches if n0 < b and n1 > a]
        if not mine: segs.append(p); continue
        q = f'{work}/s{i:03d}p.mp4'
        dec = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', p, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
        enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-'] + ENC + [q],
                               stdin=subprocess.PIPE)
        n = a; rep = 0
        while True:
            buf = dec.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            g = None
            for n0, n1, get in mine:
                if n0 <= n < n1: g = get(n, f); break
            if g is not None: rep += 1
            enc.stdin.write((f if g is None else g).tobytes()); n += 1
        enc.stdin.close(); enc.wait(); dec.wait()
        assert nframes(q) == b - a, (q, nframes(q), b - a)
        print(f'segment {a / FPS:.2f}-{b / FPS:.2f}: {b - a} frames, {rep} replaced', flush=True)
        segs.append(q)
    open(f'{work}/list.txt', 'w').write(''.join(f"file '{s}'\n" for s in segs))
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{work}/list.txt', '-c', 'copy', f'{work}/v.mp4'], check=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', f'{work}/v.mp4', '-i', src, '-map', '0:v', '-map', '1:a', '-c', 'copy',
                    '-movflags', '+faststart', out], check=True)
    a, b = nframes(src), nframes(out)
    dur = lambda p: float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
    print('frames', a, b, 'duration', dur(src), dur(out), flush=True)
    assert a == b
