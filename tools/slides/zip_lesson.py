"""ملف مضغوط لشرائح درس (PNG بدقة 1920×1080): python3 zip_lesson.py K"""
import zipfile, glob, os, sys
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
for k in [int(a) for a in sys.argv[1:]]:
    out = f'{S}/slides/zips/شرائح_الدرس{k}.zip'
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_STORED) as z:
        z.write(f'{S}/slides/out/درس{k}', f'درس{k}/')
        for f in sorted(glob.glob(f'{S}/slides/out/درس{k}/*.png')):
            z.write(f, f'درس{k}/' + os.path.basename(f))
    print(k, round(os.path.getsize(out) / 1e6, 1), 'MB')
