const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 637, height: 409 }, deviceScaleFactor: 4 });
  await p.goto('file:///root/.claude/skills/synced/3677d22d-6e71-479f-845a-4326e7166740_f78b016c-697b-4b0f-bf6a-496e8efb78cc/hdat-identity/assets/logo/hdat-logo-color.svg'); await p.waitForTimeout(500);
  await p.screenshot({ path: '/tmp/claude-0/-home-user-WOMAN/b60cb907-78a5-579e-bd39-853977c0c146/scratchpad/hr/hdat_big.png', omitBackground: true });
  await b.close();
})();
