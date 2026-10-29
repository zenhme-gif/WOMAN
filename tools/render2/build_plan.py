"""خطة الدرس الثاني من «الفرق» إلى النهاية بالمحرك الجديد، وتوقيت كل صندوق من timings.json."""
import sys, json, pickle, cv2, numpy as np
sys.path.insert(0, '.')
import render2 as R
S = R.S
T = {d['page']: d['start'] for d in json.load(open(f'{S}/l2/timings.json'))}
END = 1063.40                        # نهاية الدرس قبل الخاتمة
FADE0 = 261.27                       # بداية الانتقال القديم بعد المجموعة السابقة
MERGED = {'farq': [53, 52], 'tawaf': [54, 55], 'mushaf': [56, 57]}
GROUPS = [('farq', None), ('tawaf', None), ('mushaf', None), ([58, 59, 60, 61], None), ([62, 63], None), ([64, 65], None),
          ([66, 67], None), ([68, 69], None), ([70, 71, 72, 73], None), ([74, 75], None), ([77, 78, 79, 80], None),
          ([81, 82], None), ([83, 85, 84], None), ([86, 87, 88, 89], None)]


def page(n):
    F = cv2.imread(f'{S}/pages/{n:03d}.png'); return np.vstack([F, F[-1:]])[:1080]


def build():
    groups = []
    for g, _ in GROUPS:
        if isinstance(g, str):
            pages = MERGED[g]; imgs = [cv2.imread(f'{S}/r2/steps/{g}_{k + 1}.png') for k in range(len(pages))]
            bg = np.median(imgs[0][:40, :40].reshape(-1, 3), 0).astype(np.float32)
            hd = R.Header(imgs[0], bg); its = [R.Item(im, bg, k + 1, disk_r=32) for k, im in enumerate(imgs)]
            keep = True
        else:
            pages = g; imgs = [page(n) for n in pages]
            bg = np.median(imgs[0][:40, :40].reshape(-1, 3), 0).astype(np.float32)
            hd = R.Header(imgs[0], bg); its = [R.Item(im, bg, k + 1, disk_r=38) for k, im in enumerate(imgs)]
            keep = False
        groups.append(dict(name=g if isinstance(g, str) else f'p{pages[0]}', pages=pages, header=hd, items=its,
                           starts=[T[n] for n in pages], keep=keep))
        print('built', groups[-1]['name'], flush=True)
    return groups


def timeline(groups):
    tl = R.Timeline(FADE0)
    tl.ev.append(('fade', FADE0, FADE0 + 1.2)); tl.t = FADE0 + 1.2
    report = []
    for i, G in enumerate(groups):
        end = groups[i + 1]['starts'][0] if i + 1 < len(groups) else END
        n0 = len(tl.ev)
        st = []
        R.plan_group(tl, G['header'], G['items'], G['starts'], end, keep=G['keep'], next_exists=i + 1 < len(groups), stats=st)
        G['speed'] = st
        draws = [e for e in tl.ev[n0:] if e[0] == 'draw']
        report.append((G['name'], G['starts'][0], draws[0][1], tl.t, end, G['speed']))
    return tl, report


if __name__ == '__main__':
    groups = build()
    tl, report = timeline(groups)
    for name, a, first, tend, end, sp in report:
        print(f'{name:8s} speech {a:7.1f}  draw starts {first:7.1f} (lag {first - a:+5.1f})  done {tend:7.1f}  next {end:7.1f}  slack {end - tend:+5.1f}  body speed x{[round(1/f,1) for f in sp]}')
    pickle.dump(tl.ev, open(f'{S}/r2/events.pkl', 'wb'))
    print('events', len(tl.ev), 'timeline end', round(tl.t, 2))
