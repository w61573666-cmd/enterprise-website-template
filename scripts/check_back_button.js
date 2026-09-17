/* 「返回上一級」按鈕驗證：桌面 + 手機視口、中英文、點擊跳轉、首頁不顯示、截圖 */
const { chromium, webkit } = require('playwright');
const BASE = 'http://127.0.0.1:8080/';
const SEL = '.hsst-back';

(async () => {
  const results = [];
  const ok = (name, cond, extra) => results.push([cond ? '✅' : '❌', name, extra || '']);

  const browser = await chromium.launch();

  // —— 桌面 1440 ——
  const d = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  let p = await d.newPage();
  await p.goto(BASE + 'products/white-marble.html', { waitUntil: 'load' });
  let btn = p.locator(SEL);
  await btn.waitFor({ timeout: 5000 }).catch(() => {});
  ok('ZH 系列页显示按钮', await btn.count() === 1, await btn.count() ? ('文案=' + (await btn.innerText()).trim() + ' href=' + await btn.getAttribute('href')) : '未找到');
  ok('ZH 文案=返回產品中心', (await btn.innerText()).includes('返回產品中心'));
  ok('href 指向 ../products.html', (await btn.getAttribute('href')) === '../products.html');
  const dbox = await btn.boundingBox();
  ok('桌面按钮在右侧', !!dbox && dbox.x > 720, dbox ? `x=${Math.round(dbox.x)},y=${Math.round(dbox.y)} (视口1440)` : '');
  const dbtt = await p.locator('.back-to-top').first().boundingBox().catch(() => null);
  ok('桌面按钮在回到顶部正上方（不重叠）',
     !!dbtt && !!dbox && (dbox.y + dbox.height) <= dbtt.y + 2,
     dbtt && dbox ? `按钮底=${Math.round(dbox.y + dbox.height)} 回到顶部上缘=${Math.round(dbtt.y)}` : '');
  await btn.click();
  await p.waitForLoadState('load');
  ok('点击精确跳转到 /products.html（不是 /products/products.html）', new URL(p.url()).pathname === '/products.html', p.url());

  await p.goto(BASE + 'about.html', { waitUntil: 'load' });
  btn = p.locator(SEL); await btn.waitFor({ timeout: 5000 }).catch(() => {});
  ok('根级页 about.html → 返回首頁', await btn.count() === 1 && (await btn.innerText()).includes('返回首頁') && (await btn.getAttribute('href')) === 'index.html');

  await p.goto(BASE + 'index.html', { waitUntil: 'load' });
  await p.waitForTimeout(400);
  ok('首页不显示按钮', await p.locator(SEL).count() === 0);

  await p.goto(BASE + 'projects/hotel.html', { waitUntil: 'load' });
  btn = p.locator(SEL); await btn.waitFor({ timeout: 5000 }).catch(() => {});
  ok('工程案例页 → 返回工程案例', (await btn.innerText()).includes('返回工程案例') && (await btn.getAttribute('href')) === '../projects.html');
  await d.close();

  // —— 手機 390×844（Stone 规则：必验移动端）——
  const m = await browser.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  p = await m.newPage();
  await p.goto(BASE + 'products/engineered-stone.html', { waitUntil: 'load' });
  btn = p.locator(SEL); await btn.waitFor({ timeout: 5000 }).catch(() => {});
  ok('手机端 ZH 系列页显示按钮', await btn.count() === 1);
  const vis = await btn.isVisible();
  let box = await btn.boundingBox();
  ok('手机端按钮可见', vis, box ? `位置 x=${Math.round(box.x)},y=${Math.round(box.y)},w=${Math.round(box.width)},h=${Math.round(box.height)}` : '');
  ok('手机端按钮在右下且不出屏', !!box && box.x >= 0 && box.y + box.height <= 845 && box.width < 200);
  // 手机端 WhatsApp 球在左下（premium ≤768px left:16px bottom:20px），按钮应在其正上方
  // 先接受 cookie 关掉横幅，验证「常态位置」不与球重叠
  await p.evaluate(() => localStorage.setItem('cookieConsent', 'accepted'));
  await p.reload({ waitUntil: 'load' });
  await p.waitForTimeout(400);
  btn = p.locator(SEL); await btn.waitFor({ timeout: 5000 }).catch(() => {});
  box = await btn.boundingBox();
  ok('手机端按钮可见', await btn.isVisible(), box ? `y=${Math.round(box.y)},h=${Math.round(box.height)}` : '');
  // 手机端右下：按钮垫在「回到顶部」(right 16 / bottom 80) 下方，不得重叠
  const btt = await p.locator('.back-to-top').first().boundingBox().catch(() => null);
  ok('手机端按钮位于回到顶部正上方（不重叠）',
     !!btt && !!box && (box.y + box.height) <= btt.y + 2,
     btt && box ? `按钮底=${Math.round(box.y + box.height)} 回到顶部上缘=${Math.round(btt.y)}` : '');
  // WhatsApp 球在左下（premium ≤768px left:16px），按钮在右下，不得重叠
  const wa = await p.locator('.whatsapp-float').boundingBox().catch(() => null);
  ok('手机端按钮不与左下 WhatsApp 球重叠',
     !!wa && !!box && (box.x >= wa.x + wa.width - 2),
     wa && box ? `按钮x=${Math.round(box.x)} 球右缘=${Math.round(wa.x + wa.width)}` : '');
  ok('手机端按钮不出屏、宽度合理', !!box && box.x >= 0 && box.x + box.width <= 391 && box.y + box.height <= 845 && box.width < 200);
  await p.screenshot({ path: '/tmp/backbtn-mobile.png' });

  // EN 手机
  await p.goto(BASE + 'en/products/engineered-stone.html', { waitUntil: 'load' });
  btn = p.locator(SEL); await btn.waitFor({ timeout: 5000 }).catch(() => {});
  ok('EN 手机端文案=Back to Products', (await btn.innerText()).trim() === 'Back to Products');
  ok('EN href=../products.html', (await btn.getAttribute('href')) === '../products.html');
  await p.screenshot({ path: '/tmp/backbtn-mobile-en.png' });

  // 抽屉打开时隐藏
  await p.goto(BASE + 'products/white-marble.html', { waitUntil: 'load' });
  const burger = p.locator('.nav-toggle, .hamburger, [class*="burger"]').first();
  if (await burger.count()) {
    await burger.click().catch(() => {});
    await p.waitForTimeout(500);
    const hidden = await p.locator(SEL).isHidden().catch(() => null);
    ok('抽屉打开时按钮隐藏', hidden === true);
  }
  await m.close();

  // —— 品種獨立頁（三層路徑）——
  const v = await browser.newContext({ viewport: { width: 390, height: 844 } });
  let vp = await v.newPage();
  await vp.goto(BASE + 'products/white-marble/carrara-white.html', { waitUntil: 'load' });
  btn = vp.locator(SEL); await btn.waitFor({ timeout: 5000 }).catch(() => {});
  ok('ZH 品种页显示按钮', await btn.count() === 1);
  ok('ZH 品种页文案=返回系列', (await btn.innerText()).includes('返回系列'));
  ok('ZH 品种页 href=../../products/white-marble.html',
     (await btn.getAttribute('href')) === '../../products/white-marble.html');
  await btn.click();
  await vp.waitForLoadState('load');
  ok('点击跳转到系列页', new URL(vp.url()).pathname === '/products/white-marble.html', vp.url());

  await vp.goto(BASE + 'en/products/white-marble/carrara-white.html', { waitUntil: 'load' });
  btn = vp.locator(SEL); await btn.waitFor({ timeout: 5000 }).catch(() => {});
  ok('EN 品种页文案=Back to Series', (await btn.innerText()).trim() === 'Back to Series');
  ok('EN 品种页 href=../../products/white-marble.html',
     (await btn.getAttribute('href')) === '../../products/white-marble.html');
  await v.close();

  await browser.close();
  let fail = 0;
  for (const [s, name, extra] of results) {
    if (s === '❌') fail++;
    console.log(`  ${s} ${name}${extra ? '   | ' + extra : ''}`);
  }
  console.log(`\n########## 失败项合计: ${fail} ##########`);
  process.exit(fail ? 1 : 0);
})();
