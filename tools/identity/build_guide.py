"""دليل الهوية البصرية لجمعية هداة الخيرية لتعليم العلوم الشرعية: HTML ← PDF (A4، RTL، Tajawal مضمّن)."""
import base64, sys, cv2, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/kit')
from colors import OFFICIAL, DERIVED, NEUTRAL, SEMANTIC, SERIES, rgb
S = '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad'
D = '/root/.claude/skills/synced/3677d22d-6e71-479f-845a-4326e7166740_f78b016c-697b-4b0f-bf6a-496e8efb78cc/hdat-identity'
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
AR = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')
ar = lambda x: str(x).translate(AR)
FONTS = ''.join(f"@font-face{{font-family:'Tajawal';font-weight:{w};src:url(data:font/ttf;base64,{b64(f'{D}/assets/fonts/Tajawal-{n}.ttf')}) format('truetype')}}"
                for w, n in [(400, 'Regular'), (500, 'Medium'), (700, 'Bold'), (900, 'Black')])
LOGO_C = 'data:image/svg+xml;base64,' + b64(f'{D}/assets/logo/hdat-logo-color.svg')
LOGO_W = 'data:image/svg+xml;base64,' + b64(f'{D}/assets/logo/hdat-logo-white.svg')


def png_uri(path, width):
    a = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    a = cv2.resize(a, (width, int(round(width * a.shape[0] / a.shape[1]))), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode('.png', a)
    return 'data:image/png;base64,' + base64.b64encode(buf.tobytes()).decode()


SER_LOGO = png_uri(f'{S}/kit/series/series-logo.png', 1100)
SER_DOTS = png_uri(f'{S}/kit/series/three-dots.png', 500)
SER_NAME = png_uri(f'{S}/kit/series/sheikh-name.png', 1300)
SER_COVER = 'data:image/jpeg;base64,' + base64.b64encode(cv2.imencode('.jpg', cv2.resize(cv2.imread(f'{S}/hr/pages4k/001.png'), (1280, 720), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tobytes()).decode()
SER_SLIDE = 'data:image/jpeg;base64,' + base64.b64encode(cv2.imencode('.jpg', cv2.resize(cv2.imread(f'{S}/hr/out/درس4/02.png'), (1280, 720), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])[1].tobytes()).decode()

I = dict(  # أيقونات خطية 24×24
    logo='<path d="M12 2.5 21.5 12 12 21.5 2.5 12z"/><path d="M12 7.5 16.5 12 12 16.5 7.5 12z"/>',
    palette='<circle cx="12" cy="12" r="9"/><circle cx="8" cy="10" r="1.3"/><circle cx="12" cy="7.5" r="1.3"/><circle cx="16" cy="10" r="1.3"/><path d="M12 21c-1.5 0-2-1.3-1.2-2.4.9-1.2.2-2.6-1.3-2.6H7"/>',
    type='<path d="M5 6V4.5h14V6"/><path d="M12 4.5v15"/><path d="M9 19.5h6"/>',
    shapes='<path d="M7 3.5 10.5 7 7 10.5 3.5 7z"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><circle cx="7" cy="17" r="3.5"/><path d="M14 20.5h6.5L17.2 14z"/>',
    pen='<path d="M4 20h4L19 9a2.1 2.1 0 0 0-3-3L5 17z"/><path d="M14 8l3 3"/>',
    book='<path d="M12 6.5C10 5 7 4.5 3.5 5v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5V5C17 4.5 14 5 12 6.5z"/><path d="M12 6.5v13"/>',
    screen='<rect x="3" y="4" width="18" height="12" rx="1.8"/><path d="M8.5 20h7"/><path d="M12 16v4"/>',
    mega='<path d="M3.5 10v4h3l7 4.5V5.5l-7 4.5z"/><path d="M17 9.5a3.5 3.5 0 0 1 0 5"/><path d="M6.5 14l1.2 5h2.3"/>',
    shield='<path d="M12 3 4.5 6v5.5c0 4.5 3.2 8 7.5 9.5 4.3-1.5 7.5-5 7.5-9.5V6z"/><path d="m8.8 12 2.2 2.2 4.2-4.4"/>',
    users='<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19.5c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5"/><circle cx="16.8" cy="9.5" r="2.5"/><path d="M15.8 14.6c2.5-.3 4.3 1.3 4.8 4.4"/>',
    chart='<path d="M4 4v16h16"/><path d="M8 15.5v-4"/><path d="M12 15.5V8"/><path d="M16 15.5v-6"/>',
    files='<path d="M14 3.5H7a1.8 1.8 0 0 0-1.8 1.8v13.4A1.8 1.8 0 0 0 7 20.5h10a1.8 1.8 0 0 0 1.8-1.8V8.3z"/><path d="M14 3.5v4.8h4.8"/><path d="M9 13h6M9 16.5h4"/>',
    flower='<path d="M12 3.5 14.5 9.5 20.5 12 14.5 14.5 12 20.5 9.5 14.5 3.5 12 9.5 9.5z"/>',
)
icon = lambda n, s=18, c='currentColor': f'<svg viewBox="0 0 24 24" width="{s}" height="{s}" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{I[n]}</svg>'
RHOMBI = '<svg viewBox="0 0 120 40" class="rhombi" style="transform:scaleX(-1)"><path fill="currentColor" opacity=".95" d="M20 2 33 15 20 28 7 15z"/><path fill="currentColor" opacity=".55" d="M46 6 56 16 46 26 36 16z"/><path fill="currentColor" opacity=".3" d="M70 9 78 17 70 25 62 17z"/><path fill="currentColor" opacity=".16" d="M90 11 96 17 90 23 84 17z"/></svg>'

PAGES = []
TOTAL = 10


def head(ic, title, num):
    return f'<div class="sh"><span class="sq">{icon(ic)}</span><h2>{title}</h2><span class="pill">القسم {ar(num)}</span></div>'


def foot(n):
    return f'<div class="pfoot"><img src="{LOGO_C}" class="flogo" alt="جمعية هداة الخيرية لتعليم العلوم الشرعية"><span class="pno">{ar(n)} / {ar(TOTAL)}</span></div>'


def cmyk_s(c): return '%d.%d.%d.%d' % c if c else '—'


def swatch_rows(items):
    rows = ''
    for (n, tok, hx, cm, role, src) in items:
        r, g, b = rgb(hx)
        border = 'border:1px solid var(--c-line);' if sum((r, g, b)) > 700 else ''
        rows += (f'<tr><td><span class="chip" style="background:{hx};{border}"></span></td><td class="nm"><b>{n}</b></td>'
                 f'<td class="code" dir="ltr">{hx}</td><td class="code" dir="ltr">{r} {g} {b}</td><td class="code" dir="ltr">{cmyk_s(cm)}</td><td>{role}</td></tr>')
    return rows


TH = '<tr><th></th><th>الاسم</th><th>HEX</th><th>RGB</th><th>CMYK</th><th>الاستعمال</th></tr>'

# ١ الغلاف
PAGES.append(f'''
<section class="page cover"><div class="cover-inner">
  <img src="{LOGO_W}" class="clogo" alt="جمعية هداة الخيرية لتعليم العلوم الشرعية">
  <div class="gbar"></div>
  <h1>دليل الهوية البصرية</h1>
  <p class="csub">جمعية هداة الخيرية لتعليم العلوم الشرعية</p>
  <p class="cline">الشعار · الألوان · الخطوط · العناصر · الأسلوب، مع ملحق هوية سلسلة «فقه المرأة المسلمة»</p>
  <div class="crh">{RHOMBI}</div>
  <div class="toc">
    <div class="toc-h">محتويات الدليل</div>
    {''.join(f'<div class="toc-r"><span class="ti">{icon(ic, 15)}</span><span class="tn">{ar(i)}</span><span class="tt">{t}</span><span class="tp">{ar(p)}</span></div>' for i, (ic, t, p) in enumerate([
        ('logo', 'الشعار', 2), ('palette', 'الألوان الأساسية', 3), ('palette', 'الألوان المساندة', 4), ('type', 'الخطوط', 5),
        ('shapes', 'العناصر والأيقونات', 6), ('pen', 'الأسلوب والمحتوى', 7), ('book', 'ملحق: سلسلة «فقه المرأة المسلمة»', 8), ('palette', 'ملحق: ألوان السلسلة', 9), ('files', 'المصادر ومحتويات الحزمة', 10)], 1))}
  </div>
</div></section>''')

# ٢ الشعار
PAGES.append(f'''
<section class="page">{head('logo', 'الشعار', 1)}
<p>اللُّقمة الرسمية <b>عمودية</b>: الرمز في الأعلى، ثم «جمعية هـداة الخيرية»، ثم «لتعليم العلـوم الشرعيــة». ولا يُكرَّر اسم الجمعية نصاً تحت الشعار، فاللُّقمة تحمله.</p>
<div class="two">
  <div class="lpanel light"><img src="{LOGO_C}" alt="الشعار الملون"><div class="cap">الملوّن: على الخلفيات الفاتحة فقط</div></div>
  <div class="lpanel dark"><img src="{LOGO_W}" alt="الشعار الأبيض"><div class="cap">الأبيض: على الخلفيات الداكنة</div></div>
</div>
<h3>قواعد الاستعمال</h3>
<ul class="rh">
  <li>مساحة آمنة حول الشعار لا تقل عن ارتفاع المعيّن من كل جهة.</li>
  <li>للطباعة والأحجام الكبيرة: ملفات <span dir="ltr">SVG</span> المتجهية. وللشاشة: ملفات <span dir="ltr">PNG</span> المرفقة.</li>
  <li>حافظ على النسبة الأصلية دائماً، ولا تضعه على خلفية منخفضة التباين أو مزدحمة.</li>
</ul>
<h3>استعمالات ممنوعة</h3>
<div class="three">
  <div class="bad"><div class="bx"><img src="{LOGO_C}" style="width:72%;height:60px;object-fit:fill"></div><div class="cap"><span class="no">ممنوع</span> مطّ الشعار أو تشويه نسبته</div></div>
  <div class="bad"><div class="bx" style="background:var(--c-navy)"><img src="{LOGO_C}" style="width:62%"></div><div class="cap"><span class="no">ممنوع</span> الملوّن على خلفية داكنة</div></div>
  <div class="bad"><div class="bx" style="background:#9DC0E0"><img src="{LOGO_W}" style="width:62%"></div><div class="cap"><span class="no">ممنوع</span> خلفية منخفضة التباين</div></div>
</div>
{foot(2)}</section>''')

# ٣ الألوان الأساسية
cards = ''
for (n, tok, hx, cm, role, src) in OFFICIAL:
    r, g, b = rgb(hx)
    txt = '#fff' if n != 'ذهبي' and n != 'أزرق فاتح' else 'var(--c-navy)'
    cards += (f'<div class="sw"><div class="swc" style="background:{hx};color:{txt}"><span>{n}</span></div><div class="swb">'
              f'<div class="kv"><span>HEX</span><b dir="ltr">{hx}</b></div><div class="kv"><span>RGB</span><b dir="ltr">{r} {g} {b}</b></div>'
              f'<div class="kv"><span>CMYK</span><b dir="ltr">{cmyk_s(cm)}</b></div><div class="kv"><span>الرمز</span><b dir="ltr">{tok}</b></div>'
              f'<div class="role">{role}</div></div></div>')
PAGES.append(f'''
<section class="page">{head('palette', 'الألوان الأساسية', 2)}
<p>الألوان الأربعة منصوص عليها في دليل الهوية الرسمي للجمعية (صفحة المجموعة اللونية الأساسية) بقيمها في <span dir="ltr">RGB</span> و<span dir="ltr">CMYK</span>؛ لا اجتهاد فيها.</p>
<div class="grid2">{cards}</div>
<h3>نسب الحضور اللوني</h3>
<div class="ratio"><span style="flex:65;background:var(--c-blue)"></span><span style="flex:25;background:var(--c-line)"></span><span style="flex:10;background:var(--c-gold)"></span><span style="flex:5;background:var(--c-coral)"></span></div>
<div class="legend"><span><i style="background:var(--c-blue)"></i>أزرق ٦٠ إلى ٧٠٪</span><span><i style="background:var(--c-line)"></i>محايد نحو ٢٥٪</span><span><i style="background:var(--c-gold)"></i>ذهبي حتى ١٠٪</span><span><i style="background:var(--c-coral)"></i>مرجاني حتى ٥٪</span></div>
<p class="note">الأزرق مهيمن. الذهبي للإبراز بما لا يزيد على ١٠٪، والمرجاني للتنبيه بما لا يزيد على ٥٪، ولا يكون لون الإجراء الأساسي. ولا يجتمع أكثر من لوني تمييز على سطح واحد.</p>
{foot(3)}</section>''')

# ٤ الألوان المساندة
PAGES.append(f'''
<section class="page">{head('palette', 'الألوان المساندة', 3)}
<p class="note">هذه الألوان <b>مشتقة اجتهاداً</b> لا نصّ عليها في دليل الهوية؛ إن اعتمدت الجمعية قيماً لها فهي المقدَّمة.</p>
<h3>درجات الأزرق والذهبي</h3>
<table class="ct">{TH}{swatch_rows(DERIVED)}</table>
<h3>المحايدة</h3>
<table class="ct">{TH}{swatch_rows(NEUTRAL)}</table>
<h3>الدلالية (للواجهات)</h3>
<table class="ct">{TH}{swatch_rows(SEMANTIC)}</table>
{foot(4)}</section>''')

# ٥ الخطوط
weights = ''.join(f'<div class="wrow"><span class="wl">{lbl} <span dir="ltr">{w}</span></span><span style="font-weight:{w};font-size:18pt;color:var(--c-ink)">نشر العلم النافع وتأصيل طلاب العلم</span></div>'
                  for w, lbl in [(400, 'Regular'), (500, 'Medium'), (700, 'Bold'), (900, 'Black')])
scale = [('عنوان الغلاف', '56 · 900', '34 · 900'), ('رأس قسم', '32 · 700', '22 · 900'), ('رأس بطاقة', '24 · 700', '15 · 700'),
         ('المتن ونقاط القوائم', '16 · 400 · 1.9', '14 · 400 · 1.75'), ('خلايا الجداول والأوصاف', '14 · 400', '14 · 400'), ('رقم مؤشر', '—', '19–22 · 900')]
PAGES.append(f'''
<section class="page">{head('type', 'الخطوط', 4)}
<p>الخط الرسمي <b dir="ltr">Tajawal</b> بأوزانه الأربعة، في كل النصوص. ترخيصه مفتوح (<span dir="ltr">OFL</span>)، وملفاته مرفقة في الحزمة.</p>
<div class="weights">{weights}</div>
<h3>سُلّم الأحجام</h3>
<table class="ct sc"><tr><th>المستوى</th><th>الشاشة (px · الوزن)</th><th>المطبوع A4 (pt · الوزن)</th></tr>
{''.join(f'<tr><td>{a}</td><td class="code" dir="ltr">{b}</td><td class="code" dir="ltr">{c}</td></tr>' for a, b, c in scale)}</table>
<h3>قواعد لازمة</h3>
<ul class="rh">
  <li>المتن المطبوع ١٤pt والعناوين ١٥pt قرار معتمد من الجمعية؛ إن فاض المحتوى زيدت الصفحات ولا يُصغَّر الخط.</li>
  <li>الآيات بالرسم العثماني بخط <span dir="ltr">KFGQPC Uthmanic</span> (وبديله <span dir="ltr">Amiri Quran</span>) بين قوسين مزهرين مع اسم السورة ورقم الآية، ولا تُكتب بخط تجوّل.</li>
  <li>الأرقام العربية الهندية في النصوص التحريرية. وخط تجوّل لا يحوي فاصل الآلاف العربي، فيُستعمل معها الفاصلة: ٢٧٧,٨١١.</li>
  <li>اتجاه الكتابة من اليمين لليسار في كل تخطيط، ولا تُحاذى الفقرات العربية لليسار.</li>
</ul>
{foot(5)}</section>''')

# ٦ العناصر
PAGES.append(f'''
<section class="page">{head('shapes', 'العناصر والأيقونات', 5)}
<h3>العنصر المميِّز: المعيّن</h3>
<p>مربّع مدار ٤٥ درجة، مأخوذ من بناء الشعار نفسه ومن مطبوعات الجمعية. لا تُستعمل النجمة الثمانية.</p>
<div class="two">
  <div class="demo navy"><div class="crh" style="width:52%">{RHOMBI}</div><div class="cap" style="color:#cfe2f1">شريط متدرّج: أربعة معيّنات متناقصة الحجم والشفافية</div></div>
  <div class="demo"><ul class="rh" style="margin:0"><li>نقطة قائمة: معيّن ٦px</li><li>بلون الأزرق البترولي</li><li>في القوائم والفهارس</li></ul></div>
</div>
<h3>الأيقونات</h3>
<p>خطّية رصينة مرسومة داخلياً، لا مكتبات خارجية ولا رموز تعبيرية: لوح <span dir="ltr">24×24</span>، خط <span dir="ltr">1.6</span>، أطراف ومفاصل مستديرة.</p>
<div class="icons">{''.join(f'<div class="ic"><span class="sq lg">{icon(n, 26)}</span><span>{t}</span></div>' for n, t in [('book', 'كتاب'), ('screen', 'شاشة'), ('mega', 'مكبّر صوت'), ('shield', 'درع'), ('users', 'أشخاص'), ('chart', 'رسم بياني')])}</div>
<h3>المسافات والحواف والظلال</h3>
<div class="tokens">
  <div><b>المسافات</b> أساس ٤px: <span class="code" dir="ltr">4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96</span></div>
  <div class="radii">{''.join(f'<div class="rd"><span style="border-radius:{r}px"></span><em dir="ltr">{l} {r}</em></div>' for l, r in [('sm', 6), ('md', 10), ('lg', 16), ('xl', 24)])}</div>
  <div class="shadows">{''.join(f'<div class="shd" style="box-shadow:{v}"><span dir="ltr">{k}</span></div>' for k, v in [('sm', '0 1px 3px rgba(20,58,103,.08)'), ('md', '0 4px 12px rgba(20,58,103,.08)'), ('lg', '0 18px 40px rgba(20,58,103,.14)')])}</div>
  <p class="note" style="margin-top:4mm">الظلال مائلة للأزرق، والحواف ناعمة مستديرة.</p>
</div>
{foot(6)}</section>''')

# ٧ الأسلوب والمحتوى
PAGES.append(f'''
<section class="page">{head('pen', 'الأسلوب والمحتوى', 6)}
<h3>الاسم الرسمي</h3>
<p>«<b>جمعية هداة الخيرية لتعليم العلوم الشرعية</b>» كاملاً في كل مخرَج رسمي، لا يُختصر ولا يُبدَّل. و«هداة» وحدها في السياق الجاري فقط.</p>
<h3>الشخصية</h3>
<p>عِلمية، وقورة، موثوقة، هادئة، دافئة. لا أسلوب مرحاً ولا كرتونياً.</p>
<div class="two dos">
  <div class="do"><div class="dh">دائماً</div><ul class="rh">
    <li>اتجاه من اليمين لليسار، وعكس الأيقونات الاتجاهية.</li><li>الأزرق مهيمناً، ومساحات بيضاء واسعة.</li>
    <li>الألقاب والترضّي في مواضعها: معالي/فضيلة/سماحة الشيخ، و«رحمه الله» للمتوفّى.</li><li>الآيات بالرسم العثماني مع السورة ورقم الآية.</li></ul></div>
  <div class="dont"><div class="dh">أبداً</div><ul class="rh">
    <li>أشرطة لونية أو خطوط زخرفية أسفل العناوين.</li><li>المرجاني لوناً للإجراء الأساسي.</li>
    <li>أكثر من لوني تمييز على سطح واحد.</li><li>الشعار الملوّن على خلفية داكنة.</li></ul></div>
</div>
<h3>مفردات الجمعية</h3>
<p><b>البرامج:</b> جادة المتعلم · التأسيس العقدي · فقه السلسبيل · منصة هدى للتعليم الشرعي المفتوح · قراء · رعاية الموهوبين · فقه المرأة المسلمة · واعية · قبسات · سؤالات العلوم · جرد اللالكائي · الإرشاد إلى صحيح الاعتقاد.</p>
<p><b>الإدارات:</b> المشاريع العلمية · العمليات التقنية والفنية · التسويق والتواصل · الجودة والتطوير · الموارد البشرية والمالية · الإدارة التنفيذية والسكرتارية.</p>
<p><b>عبارات الهوية:</b> «نشر العلم النافع» · «تأصيل طلاب العلم» · «منهج السلف الصالح».</p>
{foot(7)}</section>''')

# ٨ ملحق السلسلة
ser_src = [x for x in SERIES if x[5] == 'صفحات المصدر']
ser_vid = [x for x in SERIES if x[5] != 'صفحات المصدر']
mini = lambda items: ''.join(f'<div class="ms"><span class="chip" style="background:{hx};{"border:1px solid var(--c-line);" if sum(rgb(hx)) > 700 else ""}"></span><div><b>{n}</b><div class="code" dir="ltr">{hx} · {" ".join(map(str, rgb(hx)))}</div><div class="mr">{role}</div></div></div>' for (n, tok, hx, cm, role, src) in items)
PAGES.append(f'''
<section class="page">{head('book', 'ملحق: سلسلة «فقه المرأة المسلمة»', 7)}
<p>هوية السلسلة كما في شرائح الدروس المنتجة. القيم مستخرجة بالقياس من صفحات المصدر الأصلية (ألوان مسطّحة دقيقة)، وقيم قالب الفيديو تقريبية لأنه مضغوط.</p>
<div class="two">
  <figure><img src="{SER_COVER}" class="shot"><figcaption>الغلاف</figcaption></figure>
  <figure><img src="{SER_SLIDE}" class="shot"><figcaption>شريحة عنوان ومربع</figcaption></figure>
</div>
<div class="three ser">
  <div class="sbx"><img src="{SER_LOGO}" style="height:19mm"><div class="cap">شعار السلسلة</div></div>
  <div class="sbx"><img src="{SER_DOTS}" style="width:22mm"><div class="cap">النقاط الثلاث</div></div>
  <div class="sbx"><img src="{SER_NAME}" style="height:16mm"><div class="cap">اسم الشيخ بالخط</div></div>
</div>
<h3>العناصر والخطوط</h3>
<ul class="rh">
  <li>لافتة عنوان حمراء مرسومة باليد، ومربعات بيضاء بإطار أزرق، وخط تظليل أصفر، وأقراص أرقام صفراء، وزخرفة هندسية زرقاء على حافتي الغلاف.</li>
  <li>الشريط العلوي: شعار السلسلة والنقاط الثلاث يساراً، وشعار الجمعية واسم الشيخ يميناً بينهما فاصل ذهبي.</li>
  <li>نصوص «موضوعات الدرس» بخط تجوّل العريض (مطابقة بالقياس). أما خط اللافتات وخط الشرح فلم يُتعرَّف على اسميهما.</li>
</ul>
{foot(8)}</section>''')

# ٩ ألوان السلسلة
TH2 = '<tr><th></th><th>الاسم</th><th>HEX</th><th>RGB</th><th>الاستعمال</th></tr>'
def srows(items):
    o = ''
    for (n, tok, hx, cm, role, src) in items:
        r, g, b = rgb(hx); border = 'border:1px solid var(--c-line);' if r + g + b > 700 else ''
        o += f'<tr><td><span class="chip" style="background:{hx};{border}"></span></td><td class="nm"><b>{n}</b></td><td class="code" dir="ltr">{hx}</td><td class="code" dir="ltr">{r} {g} {b}</td><td>{role}</td></tr>'
    return o
PAGES.append(f'''
<section class="page">{head('palette', 'ملحق: ألوان السلسلة', 8)}
<p>ألوان سلسلة «فقه المرأة المسلمة» بالقياس المباشر. ولم تُعتمد لها قيم <span dir="ltr">CMYK</span>، فلم تُوضع لها قيم اجتهاداً.</p>
<h3>من صفحات المصدر الأصلية (دقيقة)</h3>
<table class="ct">{TH2}{srows(ser_src)}</table>
<h3>من قالب الفيديو (تقريبية، الفيديو مضغوط)</h3>
<table class="ct">{TH2}{srows(ser_vid)}</table>
<p class="note">أزرق السلسلة وأحمر لافتتها يختلفان عن أزرق الجمعية ومرجانيها في الدليل الرسمي؛ التفصيل في الصفحة التالية.</p>
{foot(9)}</section>''')

# ١٠ المصادر والخلافات ومحتويات الحزمة
PAGES.append(f'''
<section class="page">{head('files', 'المصادر ومحتويات الحزمة', 9)}
<h3>مصادر القيم</h3>
<ul class="rh">
  <li>الألوان الأربعة الأساسية وقيم <span dir="ltr">CMYK</span> والشعار المتجهي: دليل الهوية الرسمي للجمعية.</li>
  <li>الألوان المشتقة والمحايدة والدلالية وسُلّم الأحجام والمسافات: نظام التصميم المعتمد في مهارة هوية الجمعية (اجتهاد لا نص).</li>
  <li>ألوان سلسلة «فقه المرأة المسلمة»: قياس مباشر من صفحات المصدر الأصلية ومن لوح الفيديو.</li>
</ul>
<h3>خلافات ظاهرة بين المصادر (لم تُسوَّ)</h3>
<table class="ct"><tr><th>العنصر</th><th>دليل الهوية</th><th>ملف نظام التصميم الأقدم</th><th>سلسلة الدروس</th></tr>
<tr><td>الأزرق الأساسي</td><td class="code" dir="ltr">#074B7B</td><td class="code" dir="ltr">#0E477A</td><td class="code" dir="ltr">#195691</td></tr>
<tr><td>الكحلي</td><td class="code" dir="ltr">#06395E</td><td class="code" dir="ltr">#143A67</td><td>—</td></tr>
<tr><td>الأزرق الفاتح</td><td class="code" dir="ltr">#86B8E6</td><td class="code" dir="ltr">#86BCDC</td><td>—</td></tr>
<tr><td>الذهبي</td><td class="code" dir="ltr">#F7C214</td><td class="code" dir="ltr">#F2CA1B</td><td class="code" dir="ltr">#E4C548 / #F1D562</td></tr>
<tr><td>المرجاني</td><td class="code" dir="ltr">#EC6564</td><td class="code" dir="ltr">#D66062</td><td class="code" dir="ltr">#DB7475 / #D65F61</td></tr>
<tr><td>العنصر المميِّز</td><td>المعيّن</td><td>النجمة الثمانية</td><td>زخرفة هندسية</td></tr></table>
<p class="note">اعتُمدت في هذا الدليل قيم دليل الهوية الرسمي. وألوان السلسلة أقرب إلى الملف الأقدم، وبقيت كما هي في الدروس.</p>
<h3>محتويات الحزمة</h3>
<table class="ct files"><tr><th>المجلد</th><th>الملفات</th></tr>
<tr><td>الشعار</td><td><span dir="ltr">SVG</span> ملوّن وأبيض للطباعة؛ <span dir="ltr">PNG</span> شفاف بعرضين: ٣٠٠٠ بكسل و١٠٠٠ بكسل.</td></tr>
<tr><td>الألوان</td><td><span dir="ltr">ASE</span> لبرامج أدوبي، و<span dir="ltr">CSS</span> لرموز الواجهات، و<span dir="ltr">JSON</span> لكل القيم.</td></tr>
<tr><td>الخطوط</td><td>تجوّل بأوزانه الأربعة مع ترخيص <span dir="ltr">OFL</span>.</td></tr>
<tr><td>سلسلة فقه المرأة المسلمة</td><td>شعار السلسلة، والنقاط الثلاث، واسم الشيخ، وشريط الزخرفة: <span dir="ltr">PNG</span> شفاف عالي الدقة؛ وألوانها <span dir="ltr">ASE</span> و<span dir="ltr">CSS</span>.</td></tr></table>
{foot(10)}</section>''')

CSS = open(f'{S}/kit/guide.css', encoding='utf8').read()
html = f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>دليل الهوية البصرية - جمعية هداة الخيرية لتعليم العلوم الشرعية</title><style>{FONTS}{CSS}</style></head><body>{"".join(PAGES)}</body></html>'
open(f'{S}/kit/guide.html', 'w', encoding='utf8').write(html)
print('pages', len(PAGES), 'html bytes', len(html))
