"""الدرس الثاني: سجلات توقيت مصنوعة للمجموعات الجديدة (من التفريغ الصوتي ومن قياس الأصل)، تُرسم بوضع reuse."""
import sys, json, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/regroup')
import regroup as G
S = G.S
V = '/home/user/WOMAN/lessons/lesson02-taharah-hayd-nifas.mp4'
orig = lambda g: json.loads(open(f'{S}/regroup/l2_{g}.orig.log').read().splitlines()[-1])


def bands_of(pages):
    hd, its = G.build(pages)
    out = []
    for it in its:
        rs = sorted([(s.y0, s.y1) for s in it.lines if s is not None and not s.empty])
        # حدود كل سطر حتى منتصف الفراغ مع جاره
        b = []
        for i, (a, c) in enumerate(rs):
            a2 = (rs[i - 1][1] + a) // 2 if i else a
            c2 = (c + rs[i + 1][0]) // 2 if i + 1 < len(rs) else c
            b.append([int(a2), int(c2)])
        out.append(b)
    return out


def item(ring, body0, lines, bands, clear, body1=None):
    d = dict(lines=lines, bands=bands, ring=ring, body0=body0, body1=body1 or (lines[-1][1] if lines else body0), clear=clear)
    if not lines: d['nobody'] = True
    return d


def write(name, cfg, M):
    cfg = dict(video=V, keep=False, lesson=2, out=f'{S}/regroup/{name}.mp4', **cfg)
    json.dump(cfg, open(f'{S}/regroup/{name}.json', 'w'), ensure_ascii=False)
    open(f'{S}/regroup/{name}.log', 'w').write(json.dumps(M, ensure_ascii=False) + '\n')
    print(name, json.dumps(M, ensure_ascii=False)[:400])


# دخول المسجد: شريحتان
o = orig('g9'); b = bands_of([58, 59])
write('l2_n9', dict(A=320.5, F=370.6, B=371.2, pages=[58, 59], refs=[14, 15]), dict(title=o['title'], color=o['color'], items=[
    item(324.47, 328.03, [[328.4, 333.5], [333.8, 339.5]], b[0], 357.1),
    item(357.57, 359.9, [[360.2, 364.0], [364.3, 367.8]], b[1], None)]))
# الدم النازل من الحامل: حذف «خروج الدم من الحامل»، ويبقى الأول حتى حلقة التالي
o = orig('g14'); b = bands_of([70, 72, 73]); it = o['items']
i1 = dict(it[0]); i1['clear'] = it[1]['clear']; i1['bands'] = b[0]
i3 = dict(it[2]); i3['bands'] = b[1]
i4 = dict(it[3]); i4['bands'] = b[2]
write('l2_n14', dict(A=656.4, F=770.867, B=772.033, pages=[70, 72, 73], refs=[26, 28, 29]), dict(title=o['title'], color=o['color'], items=[i1, i3, i4]))
# النفاس: ثلاث شرائح
o = orig('g16'); b = bands_of([77, 78, 80])
write('l2_n16', dict(A=807.767, F=900.1, B=900.667, pages=[77, 78, 80], refs=[32, 33, 35]), dict(title=o['title'], color=o['color'], items=[
    item(811.5, 815.3, [[821.3, 826.4], [826.7, 830.0]], b[0], 872.2),
    item(872.6, 876.0, [[876.2, 880.4], [880.7, 884.8], [885.0, 887.0]], b[1], 887.5),
    item(887.9, 891.0, [[891.3, 895.6], [895.9, 898.4]], [[672, 820], [820, 884]], None)]))   # السطران متلامسان: حدّهما عند منتصف ما بين خطي القاعدة
print('bands', bands_of([58, 59]), bands_of([77, 78, 80]))
