// يرسم SVG إلى PNG بخلفية شفافة بعرض محدد: node render_svg.js in.svg out.png width [bg]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [inp, out, w, bg] = process.argv.slice(2);
  const svg = fs.readFileSync(inp, 'utf8');
  const m = svg.match(/viewBox="([\d.\s-]+)"/); const vb = m[1].trim().split(/\s+/).map(Number);
  const W = parseInt(w), H = Math.round(W * vb[3] / vb[2]);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  const html = `<html><body style="margin:0;background:${bg || 'transparent'}"><img src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" style="display:block;width:${W}px;height:${H}px"></body></html>`;
  await p.setContent(html); await p.waitForTimeout(300);
  await p.screenshot({ path: out, omitBackground: !bg, clip: { x: 0, y: 0, width: W, height: H } });
  await b.close(); console.log(out, W, H);
})();
