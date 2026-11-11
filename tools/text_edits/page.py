"""تحديث صفحة تحميل درس: تقسيم ملف 4K الجديد إلى أجزاء 14 م.ب، وتحديث قائمة الأجزاء والحجم في الصفحة.
python3 page.py K  → يطبع دفعات النشر (مسارات الأجزاء)"""
import sys, os, re, json, glob
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
NAME4 = {1: 'lesson01-taharah-wudu-ghusl-4k.mp4', 2: 'lesson02-taharah-hayd-nifas-4k.mp4', 3: 'lesson03-salah-4k.mp4', 4: 'lesson04-salah-jamaah-4k.mp4'}
AR = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
k = int(sys.argv[1])
src = f'{S}/v4k/final_new/{NAME4[k]}'
d = f'{S}/hd{k}'; pd = f'{d}/parts'
CH = 14 * 1024 * 1024
data_size = os.path.getsize(src)
old = sorted(glob.glob(f'{pd}/l{k}-*.mp4'))
for p in old: os.remove(p)
names = []
with open(src, 'rb') as f:
    i = 1
    while True:
        b = f.read(CH)
        if not b: break
        nm = f'parts/l{k}-{i:02d}.mp4'; open(f'{d}/{nm}', 'wb').write(b); names.append(nm); i += 1
h = open(f'{d}/index.html', encoding='utf8').read()
m = re.search(r'var META = (\[.*?\]);', h)
meta = json.loads(m.group(1))
old_parts = meta[0]['parts']
meta[0]['parts'] = names; meta[0]['size'] = data_size
h = h.replace(m.group(1), json.dumps(meta, ensure_ascii=False))
mb = round(data_size / 1e6)
h = re.sub(r'<span>[٠-٩]+ ميغابايت</span>', f'<span>{str(mb).translate(AR)} ميغابايت</span>', h)
open(f'{d}/index.html', 'w', encoding='utf8').write(h)
print(json.dumps(dict(parts=names, removed=[p for p in old_parts if p not in names], size=data_size, mb=mb), ensure_ascii=False))
