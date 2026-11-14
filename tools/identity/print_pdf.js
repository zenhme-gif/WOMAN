const { chromium } = require('playwright');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + inp); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(600);
  const m = await p.evaluate(() => [...document.querySelectorAll('.page')].map((e, i) => {
    const r = e.getBoundingClientRect(); let maxB = 0;
    e.querySelectorAll('*').forEach(c => { if (c.closest('.pfoot')) return; const q = c.getBoundingClientRect(); if (q.height > 0) maxB = Math.max(maxB, q.bottom - r.top); });
    const f = e.querySelector('.pfoot'); const fTop = f ? f.getBoundingClientRect().top - r.top : r.height;
    return { page: i + 1, contentBottom_mm: +(maxB / 96 * 25.4).toFixed(1), footerTop_mm: +(fTop / 96 * 25.4).toFixed(1), scroll_mm: +(e.scrollHeight / 96 * 25.4).toFixed(1) };
  }));
  console.log(JSON.stringify(m));
  const imgs = await p.evaluate(() => [...document.querySelectorAll('img.clogo, img.flogo, .lpanel img')].slice(0, 4).map(i => [i.className, (i.offsetWidth / i.offsetHeight).toFixed(3), (i.naturalWidth / i.naturalHeight).toFixed(3)]));
  console.log('logo aspect (shown vs natural)', JSON.stringify(imgs));
  await p.pdf({ path: out, format: 'A4', printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
  await b.close();
})();
