"""ملف PDF لكل درس: شرائحه بدقة 3840×2160 مضمّنة بلا ضغط مُفقِد، بصفحات 16:9."""
import img2pdf, glob, os
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
NAMES = {1: 'الدرس الأول', 2: 'الدرس الثاني', 3: 'الدرس الثالث', 4: 'الدرس الرابع'}
os.makedirs(f'{S}/hr/pdf', exist_ok=True)
lay = img2pdf.get_layout_fun((img2pdf.in_to_pt(13.333), img2pdf.in_to_pt(7.5)))
import sys
for k in ([int(a) for a in sys.argv[1:]] or (1, 2, 3, 4)):
    fs = sorted(glob.glob(f'{S}/hr/out/درس{k}/*.png'))
    out = f'{S}/hr/pdf/شرائح {NAMES[k]} - فقه المرأة المسلمة.pdf'
    with open(out, 'wb') as fh:
        fh.write(img2pdf.convert(fs, layout_fun=lay, title=f'شرائح {NAMES[k]} - فقه المرأة المسلمة'))
    print(k, len(fs), round(os.path.getsize(out) / 1e6, 1), 'MB', out)
