import subprocess, numpy as np, sys
a, b = sys.argv[1], sys.argv[2]
W, H = 480, 270           # مقارنة بدقة مصغّرة تكفي لكشف أي إزاحة أو خلل
pa = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', a, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
pb = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-i', b, '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE)
i = 0; bad = []
while True:
    x = pa.stdout.read(W * H); y = pb.stdout.read(W * H)
    if len(x) < W * H or len(y) < W * H:
        print('end', i, 'lenA', len(x), 'lenB', len(y)); break
    d = np.abs(np.frombuffer(x, np.uint8).astype(int) - np.frombuffer(y, np.uint8).astype(int))
    m = d.max(); 
    if m > 30: bad.append((round(i / 30, 2), int(m), int((d > 30).sum())))
    i += 1
print('frames', i, 'frames differing >30:', len(bad))
if bad: print(' first', bad[:3], ' last', bad[-3:], ' time span', bad[0][0], '-', bad[-1][0])
