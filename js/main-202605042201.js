/* ============================================
   HENGSHENG MARBLE S&T - Main JavaScript
   Navigation, Language Switch, Animations
   Version: 2026-04-23-7
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ---------- Navbar Scroll Effect ----------
  const navbar = document.querySelector('.navbar');
  const handleScroll = () => {
    if (!navbar) return;
    if (window.scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // ---------- Mobile Menu Toggle ----------
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  // Create mobile overlay if not exists
  let overlay = document.querySelector('.nav-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'nav-overlay';
    document.body.appendChild(overlay);
  }

  function closeMobileMenu(force) {
    if (navToggle) navToggle.classList.remove('active');
    if (navLinks) navLinks.classList.remove('open');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    document.body.classList.remove('drawer-open');
    // Collapse all expanded dropdowns（强制展开态的面板除非显式 force 否则保留）
    if (navLinks) {
      navLinks.querySelectorAll('.nav-dropdown.mobile-open, .nav-dropdown.nav-open').forEach(dd => {
        if (dd.__navForceOpen && !force) return;
        dd.classList.remove('mobile-open', 'nav-open');
        dd.__navForceOpen = false;
        setPanelInline(dd, false);
        const t = dd.querySelector(':scope > a');
        if (t) t.setAttribute('aria-expanded', 'false');
      });
    }
  }

  function openMobileMenu() {
    if (navToggle) navToggle.classList.add('active');
    if (navLinks) navLinks.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    // 抽屉打开时隐藏 cookie 横幅等底部浮层：
    // cookie-banner z-index 2000 高于抽屉(999)，固定底部高约 163px，
    // 会拦截「瀏覽全部」等抽屉底部元素的点击（跳转失效的根因之一）
    document.body.classList.add('drawer-open');
  }

  if (navToggle) {
    navToggle.addEventListener('click', () => {
      if (navLinks.classList.contains('open')) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });
  }

  // Close on overlay click
  overlay.addEventListener('click', closeMobileMenu);

  // ---------- 导航下拉：触屏点击展开 / 收起（iPad 兼容，2026-09-09） ----------
  // 旧实现：innerWidth>1160 直接 return —— 导致 iPad Air/Pro 横屏(1180/1194/1366px)
  // 显示桌面导航（hover-only），触屏点按只会跳转、无法展开子菜单。
  // 新实现：按「指针能力」分流——
  //   触屏：点按 = 展开/收起，不再跳转（栏目页可经面板首项或页脚进入）；
  //   桌面鼠标：保持 hover 展开 + 点击跳转原行为不变。
  // CSS 侧：新增 .nav-open 点击态（所有断点通用），见 premium-20260902.css「iPad / 触屏导航修复」段。
  //
  // ⚠️ 2026-09-09 二次修复（「子菜单闪现后消失」）：
  // iPadOS Safari 常按「桌面网站」呈现，matchMedia 会报 (hover:hover)+(pointer:fine)，
  // 媒体查询判定不可靠。改为「事件实测」：pointerdown 的 pointerType==='touch'
  // 即给 <html> 加 .touch-nav（CSS 据此禁用 hover 展开），移除则回退桌面行为。
  const isTouchNav = window.matchMedia('(hover: none), (pointer: coarse)');
  const htmlEl = document.documentElement;
  if (isTouchNav.matches) htmlEl.classList.add('touch-nav');
  // 五次修复（真机日志实锤）：WebKit「桌面网站」模式的老 bug——真触屏 tap 的
  // pointer events 上报 pointerType 'mouse'，导致此前 pointerType!=='touch' 的
  // 守卫全部失效，preventDefault 从未执行，合成 hover/click 链路原样存活，
  // 面板被外部假 click 关闭（真机日志：OPEN | click:… 后紧跟 CLOSE | outside-click）。
  // 判定「真触屏」改为：pointerType==='touch'，或（pointerType==='mouse' 且媒体查询命中触屏）。
  function isTouchPointer(e) {
    return e.pointerType === 'touch' || (e.pointerType === 'mouse' && isTouchNav.matches);
  }
  document.addEventListener('pointerdown', function(e) {
    if (isTouchPointer(e)) htmlEl.classList.add('touch-nav');
    else if ((e.pointerType === 'mouse' || e.pointerType === 'pen') && !isTouchNav.matches) htmlEl.classList.remove('touch-nav');
  }, true);
  // pointerover 比 pointerdown 更早触发（iOS tap 事件序：
  // pointerover → pointerdown → … → 合成 hover → click），
  // 在此即点亮 .touch-nav，让 CSS 的 hover 抑制先于合成 hover 生效。
  document.addEventListener('pointerover', function(e) {
    if (isTouchPointer(e)) htmlEl.classList.add('touch-nav');
  }, true);
  // QA 测试开关：浏览器控制台设 window.FORCE_TOUCH_NAV=true 可强制走触屏分支（便于桌面端回归测试）
  function touchNavMode() { return window.FORCE_TOUCH_NAV === true || isTouchNav.matches; }

  /* ── 导航事件诊断日志（2026-09-09 四次修复）────────────────
     真机 iPad 复现「子菜单闪退」时，URL 加 #navdebug 打开可视日志，
     截图即可定位是哪个事件关掉了面板。平时仅写内存环形缓冲，零开销。 */
  window.__navLog = [];
  var navDebugBox = null;
  if (/(^|\?)navdebug=1|#navdebug/.test(location.search + location.hash) && document.body) {
    navDebugBox = document.createElement('pre');
    navDebugBox.id = 'nav-debug-box';
    navDebugBox.style.cssText = 'position:fixed;left:6px;bottom:6px;z-index:2147483000;background:rgba(0,0,0,.88);color:#4f4;font:10px/1.35 Menlo,Consolas,monospace;padding:8px 10px;margin:0;max-width:72vw;max-height:42vh;overflow:hidden;pointer-events:none;border-radius:6px;white-space:pre-wrap;';
    document.body.appendChild(navDebugBox);
  }
  function navLog(ev, extra) {
    var line = (Date.now() % 100000) + ' ' + ev + (extra ? ' | ' + extra : '');
    window.__navLog.push(line);
    if (window.__navLog.length > 80) window.__navLog.shift();
    // 七次修复：日志写入 sessionStorage，页面重载后仍可追溯（中途再现 boot 行 = 实锤发生过重载）
    try { sessionStorage.setItem('hsst-navlog', JSON.stringify(window.__navLog)); } catch (err) {}
    if (navDebugBox) {
      var openDd = navLinks ? navLinks.querySelectorAll('.nav-dropdown.nav-open').length : 0;
      navDebugBox.textContent = 'NAV-DBG v20260909j ' + window.innerWidth + 'x' + window.innerHeight
        + ' open=' + openDd + ' touch=' + htmlEl.classList.contains('touch-nav')
        + '\n' + window.__navLog.slice(-14).join('\n');
    }
  }
  // 恢复上一页面的日志（同一标签页重载不丢证据）
  try {
    var prevLog = JSON.parse(sessionStorage.getItem('hsst-navlog') || 'null');
    if (Array.isArray(prevLog) && prevLog.length) {
      window.__navLog = prevLog.slice(-60);
      window.__navLog.push((Date.now() % 100000) + ' ── PAGE RELOAD ──');
    }
  } catch (err) {}
  navLog('boot', 'w=' + window.innerWidth + ' touchMQ=' + isTouchNav.matches);

  // 十一次修复：实时几何探针——#navdebug 模式下每 400ms 对展开面板采样一行：
  //   visualViewport.scale > 1 = 页面被双击缩放（iPad 第二次点按落在无 touch-action
  //   覆盖的面板空白处会触发系统双击缩放，面板其实还开着，但视口跳位 = 眼中「消失」）；
  //   elementFromPoint 实测面板中心最上层元素 = 直接点名盖板者。
  // 下一次真机截图即可一锤定音区分「被关 / 被盖 / 被缩放」。
  if (navDebugBox) {
    setInterval(function () {
      if (!navLinks) return;
      var p = navLinks.querySelector('.nav-dropdown.nav-open > .mega-panel, .nav-dropdown.nav-open > .dropdown-panel');
      if (!p) return;
      var r = p.getBoundingClientRect();
      var cx = Math.round(r.left + r.width / 2), cy = Math.round(r.top + r.height / 2);
      var topEl = document.elementFromPoint(cx, cy);
      var cs = getComputedStyle(p);
      var vs = window.visualViewport ? window.visualViewport.scale : 1;
      var tag = topEl ? (topEl.tagName + '.' + (topEl.className && topEl.className.split ? String(topEl.className).split(' ')[0] : '')) : 'null';
      navLog('GEO', 'scale=' + vs.toFixed(2)
        + ' rect=' + Math.round(r.left) + ',' + Math.round(r.top) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)
        + ' top=' + tag + ' op=' + cs.opacity + ' vis=' + cs.visibility);
    }, 400);
  }

  // 七次修复：展开状态记忆。若「漏网 click 触发本页重载」（關於我們 的 href 就是
  // 当前页，重载后面板消失 ≈ 用户看到的「约一秒后自动消失」），加载后立即恢复
  // 展开状态，用户无感。用户主动收起时清除记忆。
  var NAV_MEM_KEY = 'hsst-nav-open';
  function navMemSave(idx) { try { sessionStorage.setItem(NAV_MEM_KEY, String(idx)); } catch (err) {} }
  function navMemClear() { try { sessionStorage.removeItem(NAV_MEM_KEY); } catch (err) {} }
  // 十二次修复（2026-09-13）：点按父菜单展开/切换子菜单后，浏览器会在布局回流后于
  // 「刚出现的面板」坐标上补发一次 click。该 click 落在子链接(.mega-panel-link)上会被误判为
  // 「点击子菜单」而跳转（手机端切换父菜单跳到子页面、平板同类缺陷）。记下最近一次点按展开的时刻，
  // 在极短窗口内吞掉落在展开面板内部的这次补偿 click，避免误跳；用户刻意点子链接(>600ms)仍正常跳转。
  var navJustToggled = 0;

  // 打开宽限期。面板刚展开的 800ms 内，任何非用户主动的关闭源
  // （外部 click、resize、orientationchange——含 iOS 双发 click 落在文档上、
  // 九次修复（真机日志定案）：v=h 日志显示面板在展开后 1.4s 内被「第三次点按触发器」
  // 收起（81902 OPEN → 83273 CLOSE|pup）——用户点完菜单后手指又碰到标题，切换逻辑
  // 立即收起，导致「来不及点子菜单」。改为双窗口：
  //   触发器重复点按忽略窗口 2s——展开后 2s 内再点同一标题 = 忽略（面板保持，够时间移指子菜单）；
  //   外部点击幻影过滤窗口 0.5s——展开初期落在外部的杂散点击忽略，之后的真实外部点击立即收起。
  var NAV_TRIGGER_DEBOUNCE = 2000;
  var NAV_OUTSIDE_GRACE = 500;
  function inTriggerDebounce(dd) {
    return dd.__navOpenedAt && (Date.now() - dd.__navOpenedAt) < NAV_TRIGGER_DEBOUNCE;
  }
  function inOpenGrace(dd) {
    return dd.__navOpenedAt && (Date.now() - dd.__navOpenedAt) < NAV_OUTSIDE_GRACE;
  }
  function anyOpenInGrace() {
    if (!navLinks) return false;
    var open = navLinks.querySelectorAll('.nav-dropdown.nav-open, .nav-dropdown.mobile-open');
    for (var i = 0; i < open.length; i++) { if (inOpenGrace(open[i])) return true; }
    return false;
  }

  // 八次修复：行内 !important 直写面板可见性——真机 iPad 实锤「类名在、JS 认为开着，
  // 但屏幕上被某条触屏媒体查询隐藏规则藏掉」。行内 !important 优先级高于一切样式表，
  // 物理上杜绝再被 CSS 藏掉。收起时清除行内样式，交还样式表控制。
  function setPanelInline(dropdown, on) {
    var panel = dropdown.querySelector('.mega-panel') || dropdown.querySelector('.dropdown-panel');
    if (!panel) return;
    panel.style.cssText = on
      ? 'visibility:visible!important;opacity:1!important;pointer-events:auto!important;z-index:2147483000!important;'
      : '';
  }

  // 六次修复：强制展开态。触屏 tap 展开的面板打上 __navForceOpen 标记后，
  // 一切「自动关闭源」（外部假 click、resize、orientationchange、closeMobileMenu）
  // 都关不掉它；只有用户主动操作（再点触发器、点面板链接、Esc、切换其它菜单，
  // 即调用时显式传 force=true）才能收起。桌面鼠标路径不经过 toggleDropdown，不受影响。
  function closeAllDropdowns(except, why, force) {
    if (!navLinks) return;
    var closed = false;
    navLinks.querySelectorAll('.nav-dropdown.nav-open, .nav-dropdown.mobile-open').forEach(dd => {
      if (dd === except) return;
      if (dd.__navForceOpen && !force) { navLog('KEEP', why || 'forced'); return; }
      closed = true;
      dd.classList.remove('nav-open', 'mobile-open');
      dd.__navForceOpen = false;
      setPanelInline(dd, false);
      const t = dd.querySelector(':scope > a');
      if (t) t.setAttribute('aria-expanded', 'false');
    });
    if (closed && why) navLog('CLOSE', why);
  }

  function toggleDropdown(trigger, dropdown, via) {
    const wasOpen = dropdown.classList.contains('nav-open') || dropdown.classList.contains('mobile-open');
    const label = (trigger.textContent || '').trim().slice(0, 8);
    // 修复（2026-09-13）：实现真正的开/关切换。已展开时再次点按父菜单即收起，
    // 满足「首次点击展开、再次点击收起」的需求（手机/平板/桌面抽屉态通用）。
    // 收起仍保留原有路径：点子菜单项 / 切换其它菜单 / 点空白处 / Esc。
    if (wasOpen) {
      dropdown.classList.remove('nav-open', 'mobile-open');
      dropdown.__navForceOpen = false;
      setPanelInline(dropdown, false);
      const t = dropdown.querySelector(':scope > a');
      if (t) t.setAttribute('aria-expanded', 'false');
      try {
        if (typeof dropdown.__navIdx === 'number') {
          const saved = parseInt(sessionStorage.getItem(NAV_MEM_KEY) || 'NaN', 10);
          if (saved === dropdown.__navIdx) navMemClear();
        }
      } catch (err) {}
      navLog('CLOSE', via + ':' + label + ' (toggle)');
      return;
    }
    // 切换到其它菜单 = 用户主动操作，强制收起其余面板
    closeAllDropdowns(dropdown, via + ':switch', true);
    dropdown.classList.add('nav-open', 'mobile-open');
    dropdown.__navOpenedAt = Date.now();
    dropdown.__navForceOpen = true;
    setPanelInline(dropdown, true);
    trigger.setAttribute('aria-expanded', 'true');
    htmlEl.classList.add('touch-nav'); // 保险：触屏会话确保 hover 抑制持续生效
    if (typeof dropdown.__navIdx === 'number') navMemSave(dropdown.__navIdx);
    navJustToggled = Date.now();
    navLog('OPEN', via + ':' + label);
    // 展开动画结束后，把子面板滚入抽屉可视区（≤1160 抽屉模式）
    setTimeout(function () {
      var panel = dropdown.querySelector('.mega-panel') || dropdown.querySelector('.dropdown-panel');
      if (panel && navLinks.classList.contains('open')) panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 380);
  }

  if (navLinks) {
    navLinks.querySelectorAll('.nav-dropdown > a').forEach((trigger, idx) => {
      // 记录序号（供重载后恢复展开状态用）
      const dd0 = trigger.closest('.nav-dropdown');
      if (dd0) dd0.__navIdx = idx;
      // 无障碍标注（触发器本体是链接，保留链接语义，用 aria-haspopup/aria-expanded 声明弹出关系）
      if (!trigger.hasAttribute('aria-haspopup')) trigger.setAttribute('aria-haspopup', 'true');
      if (!trigger.hasAttribute('aria-expanded')) trigger.setAttribute('aria-expanded', 'false');

      // 四次修复：触屏 tap 的事件模型整体换掉——
      // pointerdown 即 preventDefault，掐断 WebKit 的合成 hover / click /
      // 双击缩放整条链路（这是「闪现即逝」所有可能来源的总闸）；
      // 真正的展开/收起放在 pointerup 里自己做。
      trigger.addEventListener('pointerdown', function(e) {
        if (!isTouchPointer(e)) return;
        navLog('pdown', 'prevent');
        e.preventDefault(); // 屏蔽兼容鼠标事件（合成 hover/mouseup/click/双击缩放）
      });

      trigger.addEventListener('pointerup', function(e) {
        if (!isTouchPointer(e) && !window.FORCE_TOUCH_NAV) return;
        navLog('pup', (e.pointerType || '?'));
        const dropdown = this.closest('.nav-dropdown');
        dropdown.__touchToggledAt = Date.now();
        toggleDropdown(this, dropdown, 'pup');
      });

      // click 双保险：被 pointerdown preventDefault 后，Webkit/Chromium 均不再派发 click；
      // 若个别内核仍派发，700ms 内跟随 pointerup 切换的 click 一律只阻断跳转、不重复切换。
      trigger.addEventListener('click', function(e) {
        const dropdown = this.closest('.nav-dropdown');
        if (Date.now() - (dropdown.__touchToggledAt || 0) < 700) {
          navLog('click-skip', 'after-pup');
          e.preventDefault();
          return;
        }
        // 触屏判定：click 自带 pointerType（部分内核），或会话内出现过触屏交互（.touch-nav），
        // 或媒体查询命中，或抽屉菜单已展开（桌面浏览器缩窄至断点以下、用鼠标点按父菜单也要展开子菜单）
        // ——四者任一即按「展开/收起」处理；否则桌面鼠标保持原行为（hover 展开、点击跳转）。
        // 修复：此前仅认触屏指针，导致「桌面浏览器窗口未全屏、宽度 < 断点」时点击父菜单子菜单无法显示。
        const mobileMode = navLinks && navLinks.classList.contains('open');
        const touchClick = e.pointerType === 'touch'
          || htmlEl.classList.contains('touch-nav')
          || touchNavMode()
          || mobileMode;
        if (!touchClick) return;
        navLog('click-toggle');
        e.preventDefault();
        e.stopPropagation();
        toggleDropdown(this, dropdown, 'click');
      });

      // 键盘无障碍：Enter / Space 切换，Esc 收起
      trigger.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          this.click();
        }
      });
    });

    // 点击面板内链接后收起全部子菜单（用户主动选择，强制收起）
    navLinks.querySelectorAll('.mega-panel-link, .dropdown-item').forEach(link => {
      link.addEventListener('click', () => { navMemClear(); closeAllDropdowns(null, 'panel-link', true); });
    });

    // 点击导航以外区域：收起全部子菜单。十一次修复：点击坐标落在任一展开面板
    // 外扩 28px 矩形内 = 用户手指在面板附近的误触/擦边，不关闭（iPad 手指宽，
    // 点完标题抬指常落在导航条下边缘之外，此前直接被当外部点击强制收起）。
    document.addEventListener('click', function(e) {
      if (e.target.closest('.navbar')) return;
      if (anyOpenInGrace()) return;
      var openPanels = navLinks.querySelectorAll('.nav-dropdown.nav-open > .mega-panel, .nav-dropdown.nav-open > .dropdown-panel');
      for (var i = 0; i < openPanels.length; i++) {
        var r = openPanels[i].getBoundingClientRect();
        if (e.clientX >= r.left - 28 && e.clientX <= r.right + 28 && e.clientY >= r.top - 28 && e.clientY <= r.bottom + 28) {
          navLog('outside-skip', 'near-panel');
          return;
        }
      }
      navMemClear(); closeAllDropdowns(null, 'outside-click', true);
    });
    // 十二次修复（续）：捕获阶段吞掉「点按展开后回流补偿的 click」。
    // 该 click 落在刚展开面板的子链接上会误跳转；窗口 600ms（短于用户刻意点子链接的间隔），
    // 仅作用于面板内部，不影响抽屉外点击 / 刻意点子链接。
    document.addEventListener('click', function(e) {
      if (navJustToggled && (Date.now() - navJustToggled) < 600) {
        if (e.target.closest('.mega-panel, .dropdown-panel')) {
          navLog('click-swallow', 'panel-after-toggle');
          e.preventDefault();
          e.stopPropagation();
          return;
        }
      }
    }, true);
    // Esc：收起子菜单并关闭抽屉（用户主动操作，强制收起）
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') { navMemClear(); closeAllDropdowns(null, 'esc', true); closeMobileMenu(true); }
    });
    // 横竖屏切换 / 窗口尺寸变化：收起子菜单，避免断点切换后布局错乱
    // （打开宽限期内忽略——iOS 工具栏收展的假 resize / 旋转初期抖动不误关面板）
    window.addEventListener('orientationchange', function() {
      navLog('orientchange');
      setTimeout(function() { if (!anyOpenInGrace()) closeAllDropdowns(null, 'orient'); }, 350);
    });
    let navResizeTimer, navLastW = window.innerWidth;
    window.addEventListener('resize', function() {
      clearTimeout(navResizeTimer);
      navResizeTimer = setTimeout(function() {
        // 仅在宽度变化（断点切换/旋转）时收起子菜单；
        // iOS Safari 工具栏收展会触发同宽度的 resize，不能因此关闭面板（否则菜单"闪现即逝"）
        if (window.innerWidth !== navLastW) {
          navLog('resize', navLastW + '→' + window.innerWidth);
          if (!anyOpenInGrace()) closeAllDropdowns(null, 'resize-w');
          navLastW = window.innerWidth;
        }
      }, 250);
    });

    // 七次修复：页面加载后恢复上次的展开状态（对抗「漏网 click 触发本页重载」，
    // 重载后面板立即重现，用户无感）。仅触屏会话生效；用户主动收起时已清除记忆。
    try {
      var savedIdx = parseInt(sessionStorage.getItem(NAV_MEM_KEY), 10);
      if (!isNaN(savedIdx)) {
        var ddSaved = navLinks.querySelectorAll('.nav-dropdown')[savedIdx];
        var trigSaved = ddSaved && ddSaved.querySelector(':scope > a');
        if (trigSaved) {
          navLog('restore', 'idx=' + savedIdx);
          toggleDropdown(trigSaved, ddSaved, 'restore');
        }
      }
    } catch (err) {}
  }

  // Close menu on regular nav link click (not dropdown triggers)
  if (navLinks) {
    navLinks.querySelectorAll('a:not(.nav-dropdown > a):not(.lang-switch a):not(.mega-panel-link):not(.dropdown-item)').forEach(link => {
      link.addEventListener('click', () => {
        closeMobileMenu();
      });
    });
  }

  // ---------- Mega-Panel 子菜单 ----------
  // 2026-09-06：旧版 3×3 折叠逻辑（子项 >9 时隐藏多余项并把 viewall 改为开关）
  // 已移除；其后 viewall 入口亦已全站删除（子项全量直出，无需二次入口）。
  // mega-panel-v2 removed; all pages now use unified mega-panel pattern

  // ---------- Series Card Click Handler (All versions) ----------
  // Handles both Chinese (.series-card-link) and English (a.series-overview-card) cards
  // Capture phase to beat lightbox handler; CSS touch-action:manipulation removes 300ms delay
  function handleSeriesCardClick(e) {
    var link = e.target.closest('a.series-card-link, a.series-overview-card');
    if (!link) return;
    var href = link.getAttribute('href');
    if (!href || !href.startsWith('#')) return;
    var target = document.querySelector(href);
    if (!target) return;
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    // Close mobile menu only if it's open (check navToggle state)
    if (navToggle && navToggle.classList.contains('active')) {
      closeMobileMenu();
    }
    // Immediate scroll, no delay - more reliable across browsers
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  document.addEventListener('click', handleSeriesCardClick, true);

  // ---------- Scroll Animations (Intersection Observer) ----------
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

/* [REMOVED DEAD] Product Filter — no .filter-btn or .product-card in HTML */


/* [KEPT] Contact Form — alert-based, keep for basic functionality */

  // ---------- Smooth scroll for anchor links ----------
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      // Skip series cards (handled by dedicated handler above)
      if (this.classList.contains('series-card-link') || this.classList.contains('series-overview-card')) return;
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        // Close mobile menu and dropdowns before scrolling
        closeMobileMenu();
        document.querySelectorAll('.nav-dropdown').forEach(dd => { dd.classList.remove('mobile-open', 'nav-open'); const t = dd.querySelector(':scope > a'); if (t) t.setAttribute('aria-expanded', 'false'); });
        // Small delay to let menu close before scroll starts
        setTimeout(() => {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 50);
      }
    });
  });

});

// ---------- Fade In Up Animation Keyframe ----------
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;
document.head.appendChild(style);

// ── Universal Image Click-to-Zoom (Event Delegation) ──────────────────────
// Uses event delegation on document so clicks work even when overlays/pseudo-elements block direct binding

document.addEventListener('DOMContentLoaded', function() {

  // ── Collect all zoomable image sources on the page ──
  function getAllZoomableImages() {
    var results = [];
    // A) <img> tags in content areas
    document.querySelectorAll('#main-content img, .hero img, .section-padding img, .trust-bar img, .about-preview img, .products-page img, .stone-card-img img, .product-cat-image img, .gallery-item img, .masonry-item img, .card-img img, .masonry-img img').forEach(function(img) {
      if (!img.src || img.src.indexOf('data:') === 0) return;
      if (img.src.indexOf('logo-hsst') !== -1) return;
      if (isExcluded(img)) return;
      if (img.naturalWidth > 0 && img.naturalWidth < 80) return;
      results.push({ src: img.src, alt: img.alt || 'Image' });
    });
    // B) Background-image elements
    document.querySelectorAll('.scenario-card-bg, .news-card-image .bg, .about-image, .project-card, .featured-project-card .card-bg').forEach(function(el) {
      var bgSrc = getBgSrc(el);
      if (bgSrc) results.push({ src: bgSrc, alt: el.getAttribute('aria-label') || 'Image' });
    });
    return results;
  }

  function isExcluded(el) {
    var excludeSelectors = '.nav-logo, .mega-panel-icon, .partner-logo, .cert-badge, footer, nav, .nav-overlay, .stone-card-zoom, [class*="icon"], [class*="badge"], img[alt="HSST"]';
    return el.closest(excludeSelectors) !== null;
  }

  function getBgSrc(el) {
    var bgMatch = (el.style.backgroundImage || getComputedStyle(el).backgroundImage || '').match(/url\(['"]?([^'"]+)['"]?\)/);
    return bgMatch ? bgMatch[1] : null;
  }

  // ── Lightbox ──
  function openImageLightbox(src, alt) {
    var allImgs = getAllZoomableImages();
    var currentIndex = allImgs.findIndex(function(item) { return item.src === src || item.src.replace(/\?.*/, '') === src.replace(/\?.*/, ''); });
    if (currentIndex < 0) currentIndex = 0;

    var modal = document.createElement('div');
    modal.className = 'image-modal active';
    modal.dataset.index = currentIndex;
    modal.innerHTML =
      '<div class="image-modal-overlay"></div>' +
      '<div class="image-modal-content" style="max-width:92vw;max-height:90vh;">' +
        '<button class="image-modal-prev" type="button" aria-label="Previous image / 上一张" style="display:' + (allImgs.length > 1 ? 'flex' : 'none') + ';">&#8592;</button>' +
        '<button class="image-modal-next" type="button" aria-label="Next image / 下一张" style="display:' + (allImgs.length > 1 ? 'flex' : 'none') + ';">&#8594;</button>' +
        '<button class="image-modal-close" type="button" aria-label="Close preview / 关闭预览"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false"><path d="M5.5 5.5 L18.5 18.5 M18.5 5.5 L5.5 18.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/></svg></button>' +
        '<img src="' + src + '" alt="' + alt + '" style="max-width:88vw;max-height:82vh;object-fit:contain;border-radius:8px;">' +
        '<div style="text-align:center;color:rgba(255,255,255,0.7);font-size:0.8rem;margin-top:8px;">' + alt + '</div>' +
      '</div>';
    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';

    var imgEl = modal.querySelector('img');
    var prevBtn = modal.querySelector('.image-modal-prev');
    var nextBtn = modal.querySelector('.image-modal-next');

    function close() { modal.remove(); document.body.style.overflow = ''; }
    modal.querySelector('.image-modal-close').onclick = close;
    modal.querySelector('.image-modal-overlay').onclick = close;

    function navigate(dir) {
      var idx = parseInt(modal.dataset.index) + dir;
      if (idx < 0) idx = allImgs.length - 1;
      if (idx >= allImgs.length) idx = 0;
      modal.dataset.index = idx;
      imgEl.src = allImgs[idx].src;
      imgEl.alt = allImgs[idx].alt || '';
    }
    if (prevBtn) prevBtn.onclick = function() { navigate(-1); };
    if (nextBtn) nextBtn.onclick = function() { navigate(1); };

    function onKey(e) {
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') navigate(-1);
      if (e.key === 'ArrowRight') navigate(1);
    }
    document.addEventListener('keydown', onKey);
    modal._removeKey = function() { document.removeEventListener('keydown', onKey); };
  }

  // Expose globally for other code
  window.openImageLightbox = openImageLightbox;

  // ── Event Delegation: catch ALL clicks on the document ──
  document.addEventListener('click', function(e) {
    // Don't intercept clicks inside lightbox
    if (e.target.closest('.image-modal')) return;

    // Don't intercept nav/footer clicks
    if (e.target.closest('nav, footer, .nav-overlay, .nav-toggle, .lang-switch, .mega-panel')) return;

    // Don't intercept button/link clicks (we only want image clicks)
    if (e.target.closest('a:not(.series-card-link):not(.series-overview-card):not(.scenario-card):not(.stone-card):not(.gallery-item):not(.masonry-item):not(.featured-project-card), button, .btn, .nav-toggle')) return;

    var src = null;
    var alt = 'Image';

    // 1) Direct <img> click
    var img = e.target.closest('img');
    if (img && !isExcluded(img)) {
      if (img.src && img.src.indexOf('data:') !== 0 && img.src.indexOf('logo-hsst') === -1) {
        if (!img.naturalWidth || img.naturalWidth >= 80) {
          src = img.src;
          alt = img.alt || 'Image';
        }
      }
    }

    // 2) Click on container with background-image
    if (!src) {
      var bgSelectors = '.scenario-card-bg, .news-card-image .bg, .about-image, .project-card, .featured-project-card .card-bg';
      var bgEl = e.target.closest(bgSelectors);
      if (bgEl) {
        src = getBgSrc(bgEl);
        alt = bgEl.getAttribute('aria-label') || 'Image';
      }
    }

    // 3) Click on .scenario-card → get background from .scenario-card-bg
    if (!src) {
      var card = e.target.closest('.scenario-card');
      if (card) {
        var bg = card.querySelector('.scenario-card-bg');
        if (bg) {
          src = getBgSrc(bg);
          alt = card.querySelector('h3') ? card.querySelector('h3').textContent : 'Image';
        }
      }
    }

    // 4) Click on .stone-card or .stone-card-img → get inner <img>
    if (!src) {
      var stoneCard = e.target.closest('.stone-card, .stone-card-img');
      if (stoneCard) {
        var sImg = stoneCard.querySelector('img');
        if (sImg && !isExcluded(sImg)) {
          src = sImg.src;
          alt = sImg.alt || 'Stone Sample';
        }
      }
    }

    // 5) Click on .featured-project-card → get background from .card-bg
    if (!src) {
      var fpc = e.target.closest('.featured-project-card');
      if (fpc) {
        var cbg = fpc.querySelector('.card-bg');
        if (cbg) {
          src = getBgSrc(cbg);
          alt = 'Project Case';
        }
      }
    }

    // 6) Gallery / masonry items
    if (!src) {
      var galItem = e.target.closest('.gallery-item, .masonry-item');
      if (galItem) {
        var gImg = galItem.querySelector('img');
        if (gImg) {
          src = gImg.src;
          alt = gImg.alt || 'Image';
        }
      }
    }

    // If we found an image, open lightbox
    if (src) {
      e.preventDefault();
      e.stopPropagation();
      openImageLightbox(src, alt);
    }
  }, true); // capture phase to catch before overlay stops propagation

  // ── Set cursor: zoom-in on all zoomable images ──
  function setCursors() {
    document.querySelectorAll('#main-content img, .hero img, .section-padding img, .about-preview img, .stone-card-img img, .product-cat-image img, .gallery-item img, .masonry-item img').forEach(function(img) {
      if (isExcluded(img)) return;
      if (img.src && img.src.indexOf('data:') !== 0 && img.src.indexOf('logo-hsst') === -1) {
        if (!img.naturalWidth || img.naturalWidth >= 80) {
          img.style.cursor = 'zoom-in';
        }
      }
    });
    document.querySelectorAll('.scenario-card-bg, .about-image, .featured-project-card, .gallery-item, .masonry-item, .stone-card, .stone-card-img, .scenario-card').forEach(function(el) {
      el.style.cursor = 'zoom-in';
    });
  }
  setCursors();
  // Re-apply after AOS animations might change things
  setTimeout(setCursors, 1500);
});

// ═══════════════════════════════════════════
// P2: 动画与交互增强
// ═══════════════════════════════════════════

// ── 初始化 AOS ──
(function initAOS() {
  var script = document.createElement('script');
  script.src = 'https://unpkg.com/aos@2.3.4/dist/aos.js';
  script.onload = function() { AOS.init({ duration: 700, easing: 'ease-out-cubic', once: true, offset: 60, disable: 'phone' }); };
  document.head.appendChild(script);
})();

// ── 数字计数动画 ──
function animateCounter(el, target, suffix, duration) {
  if (el.dataset.animated) return;
  el.dataset.animated = 'true';
  var fmt = function(n){ return String(Math.floor(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ','); };
  var start = 0;
  var step = target / (duration / 16);
  var tick = function() {
    start += step;
    if (start >= target) {
      el.textContent = fmt(target) + (suffix || '');
      el.classList.remove('counting');
      el.classList.add('counted');
      var parent = el.closest('.stat-item, .trust-item');
      if (parent) parent.classList.add('counted');
    } else {
      el.textContent = fmt(start) + (suffix || '');
      requestAnimationFrame(tick);
    }
  };
  el.classList.add('counting');
  requestAnimationFrame(tick);
}

// ── IntersectionObserver：数字计数触发 ──
var counterObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      var el = entry.target;
      var text = el.textContent.trim();
      var suffix = text.replace(/[\d.,\s-]/g, '');
      var target = parseInt(text.replace(/[.,\s]/g, ''), 10);
      if (!isNaN(target)) animateCounter(el, target, suffix, 1800);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-number, .trust-number').forEach(function(el) {
  counterObserver.observe(el);
});

// ── IntersectionObserver：stat-item/trust-item 入场动画 ──
var itemObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      var items = entry.target.querySelectorAll ? entry.target.querySelectorAll('.stat-item, .trust-item') : [entry.target];
      items.forEach(function(item, i) {
        setTimeout(function() { item.classList.add('counted'); }, i * 150);
      });
      itemObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });

document.querySelectorAll('.about-stats, .trust-items, .trust-bar').forEach(function(el) {
  itemObserver.observe(el);
});

// WhatsApp Dual Protocol - Desktop: web.whatsapp.com, Mobile: wa.me (deep link)
(function() {
  var isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || 
                 ('ontouchstart' in window) || 
                 (navigator.maxTouchPoints > 0);
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href*="wa.me"], a[href*="web.whatsapp.com"]').forEach(function(link) {
      link.addEventListener('click', function(e) {
        var phone = '+85255380525';
        if (isMobile) {
          link.href = 'https://wa.me/' + phone;
        } else {
          link.href = 'https://web.whatsapp.com/send?phone=' + phone;
        }
      }, true);
    });
  });
})();

/* ── News Modal System ─────────────────────────────────────────────── */
(function () {
  var ACTIVE = 'active';

  function getOverlay() { return document.getElementById('news-modal-overlay'); }
  function getContent() { return document.getElementById('news-modal-content'); }

  function openNewsModal(id) {
    var ov = getOverlay(), co = getContent();
    if (!ov || !co) return;
    var tpl = document.getElementById('md-' + id);
    if (!tpl) return;
    co.innerHTML = tpl.innerHTML;
    ov.classList.add(ACTIVE);
    document.body.style.overflow = 'hidden';
    sessionStorage.setItem('newsModal', id);
  }

  function closeNewsModal(e) {
    if (e && e.target !== e.currentTarget) return;
    var ov = getOverlay();
    if (ov) ov.classList.remove(ACTIVE);
    document.body.style.overflow = '';
    sessionStorage.removeItem('newsModal');
  }

  window.openNewsModal = openNewsModal;
  window.closeNewsModal = closeNewsModal;

  document.addEventListener('DOMContentLoaded', function () {
    var ov = getOverlay();
    if (ov) {
      ov.addEventListener('click', closeNewsModal);
      var cb = ov.querySelector('.news-modal-close');
      if (cb) cb.addEventListener('click', function (e) { e.stopPropagation(); closeNewsModal(); });
    }
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { var o = getOverlay(); if (o && o.classList.contains(ACTIVE)) closeNewsModal(); }
    });

    /* Auto-open modal from URL param ?modal=modal-XX */
    var params = new URLSearchParams(window.location.search);
    var m = params.get('modal');
    if (m) setTimeout(function () { openNewsModal(m); }, 150);
  });

  /* Auto-fix language switcher links to stay on current page */
  function fixLangSwitcherHrefs() {
    var switcher = document.querySelector('.lang-switch');
    if (!switcher) return;

    var links = switcher.querySelectorAll('a');
    var currentPath = window.location.pathname;

    // Detect current language from path (must start with /en/, not merely contain it)
    var isEnPage = currentPath === '/en' || currentPath.indexOf('/en/') === 0;

    links.forEach(function(link) {
      var href = link.getAttribute('href');
      var text = link.textContent.trim().toUpperCase();

      if (!href) return;

      // Use absolute root paths so any directory depth resolves correctly
      // If on EN page, determine correct TC target: /en/xxx → /xxx
      if (isEnPage && text === 'TC') {
        var tcPath = currentPath.replace(/^\/en\/?/, '/');
        if (tcPath === '/') tcPath = '/index.html';
        link.setAttribute('href', tcPath);
      }
      // If on TC page, determine correct EN target: /xxx → /en/xxx
      else if (!isEnPage && text === 'EN') {
        var enPath = (currentPath === '/' || currentPath === '/index.html')
          ? '/en/index.html'
          : '/en' + currentPath;
        link.setAttribute('href', enPath);
      }
    });
  }

  /* Persist modal state through language switch */
  function patchLangSwitcher() {
    fixLangSwitcherHrefs();
    
    var links = document.querySelectorAll('.lang-switch a');
    links.forEach(function (link) {
      link.addEventListener('click', function (e) {
        var cur = sessionStorage.getItem('newsModal');
        if (!cur) return;
        e.preventDefault();
        var href = link.getAttribute('href');
        if (!href) return;
        href = href.replace(/([?&])modal=[^&]+/g, '');
        href = href.replace(/&{2,}/g, '&');
        href = href.replace(/\?&/g, '?');
        var sep = href.includes('?') ? '&' : '?';
        window.location.href = href + sep + 'modal=' + cur;
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', patchLangSwitcher);
  } else {
    patchLangSwitcher();
  }
})();


// WhatsApp link fix: desktop uses web.whatsapp.com, mobile keeps wa.me
(function() {
  var isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  if (isMobile) return;
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href*="wa.me"]').forEach(function(link) {
      var href = link.getAttribute('href');
      var phone = href.replace(/wa\.me\/|web\.whatsapp\.com\/send\?phone=/gi, '').replace(/[^0-9+]/g, '');
      if (phone) {
        link.setAttribute('href', 'https://web.whatsapp.com/send?phone=' + phone);
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      }
    });
  });
})();


// ===== HSST Watermark: add company name to all content images & videos =====
(function() {
  var isEN = /^\/en/.test(window.location.pathname);
  var wmText = isEN ? 'HENGSHENG MARBLE S&T CO. LIMITED' : '恒生石材科技有限公司';

  // Skip these elements (logos, nav icons, footer, etc.)
  var skipSelectors = [
    '.nav-logo',
    '.mega-panel-icon',
    '.footer-logo',
    '.footer-brand',
    '.footer-social',
    '.trust-bar',
    '.whatsapp-float',
    'img[alt="HSST"]',
    '.contact-visit-map iframe',
    '.nav-center-title'
  ];

  function shouldSkip(el) {
    for (var i = 0; i < skipSelectors.length; i++) {
      try {
        if (el.matches(skipSelectors[i]) || el.closest(skipSelectors[i])) return true;
      } catch(e) {}
    }
    return false;
  }

  function ensureRelative(el) {
    // <picture> 只能作为 img 的包裹层：给它加 position 会抢占
    // 内部绝对定位 img（如 .cs2-overview-media / .v2-hero-media）的
    // containing block，导致图片塌缩为 0×0 不可见。永远跳过。
    if (!el || el.tagName === 'PICTURE') return;
    var s = getComputedStyle(el);
    if (s.position === 'static') {
      el.style.position = 'relative';
    }
  }

  function addWM(container) {
    if (!container || container.querySelector(':scope > .hsst-wm')) return;
    ensureRelative(container);
    var d = document.createElement('div');
    d.className = 'hsst-wm';
    d.textContent = wmText;
    container.appendChild(d);
  }

  // Wrap a single <img> in a position:relative div and add watermark to the wrapper
  function wrapImgWithWM(img) {
    if (img.dataset.hsstWm || shouldSkip(img)) return;
    img.dataset.hsstWm = '1';
    var w = img.offsetWidth || img.naturalWidth || 0;
    var h = img.offsetHeight || img.naturalHeight || 0;
    if (w > 0 && w < 50) return;
    if (h > 0 && h < 50) return;

    var wrapper = document.createElement('div');
    wrapper.style.cssText = 'position:relative;overflow:hidden;border-radius:inherit;';
    // Preserve grid-column span for first-child in product-cat-image
    if (img === img.parentElement.firstElementChild) {
      wrapper.style.gridColumn = 'span 2';
    }
    img.parentNode.insertBefore(wrapper, img);
    wrapper.appendChild(img);
    addWM(wrapper);
  }

  function processImg(img) {
    if (img.dataset.hsstWm || shouldSkip(img)) return;
    img.dataset.hsstWm = '1';
    var w = img.offsetWidth || img.naturalWidth || 0;
    var h = img.offsetHeight || img.naturalHeight || 0;
    if (w > 0 && w < 50) return;
    if (h > 0 && h < 50) return;

    // Multi-image containers: wrap each image individually for per-image watermark
    var multiImgContainer =
      img.closest('.product-cat-image') ||
      null;
    if (multiImgContainer) {
      wrapImgWithWM(img);
      return;
    }

    // Single-image container types — add watermark to the container
    var container =
      img.closest('.stone-card-img') ||
      img.closest('.hero-grid-item') ||
      img.closest('.news-modal-img-wrap') ||
      img.closest('.about-video-wrap') ||
      img.closest('.contact-visit-map') ||
      img.closest('.case-card-img') ||
      null;

    if (container) {
      addWM(container);
      return;
    }

    // Fallback: add watermark to parent element.
    // webp 改造后 img 常被 <picture> 包裹——水印必须落在 picture 的
    // 父级容器上（picture 自身 0×0 且不可定位），否则水印不可见，
    // 且 picture 被定位后会让绝对定位的 img 塌缩。
    var parent = img.parentElement;
    if (parent && parent.tagName === 'PICTURE') parent = parent.parentElement;
    if (parent) addWM(parent);
  }

  function processVideo(v) {
    if (v.dataset.hsstWm || shouldSkip(v)) return;
    v.dataset.hsstWm = '1';

    var container =
      v.closest('.hero-grid-item') ||
      v.closest('.about-video-wrap') ||
      null;

    if (container) {
      addWM(container);
      return;
    }

    var parent = v.parentElement;
    if (parent) addWM(parent);
  }

  function processBgImages() {
    // News card background images
    document.querySelectorAll('.news-card-image').forEach(function(nc) {
      if (nc.querySelector(':scope > .hsst-wm')) return;
      addWM(nc);
    });
  }

  function processAll() {
    // Videos
    document.querySelectorAll('video').forEach(processVideo);

    // Images
    document.querySelectorAll('img').forEach(function(img) {
      if (img.complete) {
        processImg(img);
      } else {
        img.addEventListener('load', function() { processImg(img); });
      }
    });

    // Background-image elements
    processBgImages();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processAll);
  } else {
    processAll();
  }
})();

/* 語言偏好記憶：點擊中／英切換連結時記錄選擇（供首頁語言入口判斷） */
(function(){
  function remember(v){ try { localStorage.setItem('hsst_lang', v); } catch (e) {} }
  document.addEventListener('click', function(e){
    var el = e.target;
    while (el && el !== document) {
      if (el.nodeType === 1 && el.getAttribute) {
        var v = el.getAttribute('data-lang');
        if (v === 'zh' || v === 'en') { remember(v); return; }
      }
      el = el.parentNode;
    }
  }, true);
})();



/* ===== 网格引擎 · 内容卡片按「实卡数 + 视口」定列 =====
   桌面: 4→4列 / 5→3列(3+2) / 6→3列(3+3) / 3→3列(整行) / 7+ → 自动选无孤行列数
   平板(640-1023): 自动选 2/3/4 使末行不孤卡; 手机(<640): 1 列
   与 css/premium-20260902.css 模块21 配套 */
(function(){
  var SEL = [
    '.trust-items', '.why-choose-grid', '.about-stats', '.scenarios-grid', '.role-cards',
    '.certificates-grid', '.info-cards', '.service-cards', '.advantage-cards', '.solutions-grid',
    '.service-grid', '.pain-point-grid', '.application-grid',
    '.related-cases-grid', '.related-products-grid', '.product-video-grid',
    '.contact-core-grid', '.art-related-grid',
    '.overview-grid', '.stone-grid', '.gallery-grid', '.network-grid',
    '.why-grid', '.honor-grid', '.partner-grid', '.manufacturing-grid', '.mines-grid',
    '.esg-grid', '.industry-grid', '.jobs-grid', '.region-grid', '.strength-grid'
  ].join(',');
  function firstCol(n, list){ for(var i=0;i<list.length;i++){ var c=list[i]; if(n>=c && n%c!==1){ return c; } } return n<=4?n:2; }
  function cols(n, w){
    if(n<=1){ return 1; }
    if(w<640){ return 1; }
    if(w<1024){ return firstCol(n, [2,3,4]); }
    if(n===2){ return 2; }
    if(n===3||n===5||n===6){ return 3; }
    if(n===4){ return 4; }
    return firstCol(n, [4,3,5,2]);
  }
  function apply(){
    var els = document.querySelectorAll(SEL);
    for(var i=0;i<els.length;i++){
      var el = els[i], n = 0;
      for(var j=0;j<el.children.length;j++){
        var c = el.children[j];
        if(c.nodeType!==1){ continue; }
        /* 跳过容器内的标题/装饰（宽松启发：仅跳过独立 .*-title 行） */
        var cls = String(c.className && c.className.baseVal !== undefined ? c.className.baseVal : c.className);
        if(/^[\s]*(section-)?(block|row)-?title[\s]*$/i.test(cls) || /section-(header|title)/i.test(cls)){ continue; }
        n++;
      }
      if(n===0){ continue; }
      el.style.setProperty('--c', cols(n, window.innerWidth));
      el.style.setProperty('--c-t', cols(n, 900));
    }
  }
  var t = null;
  function onResize(){ if(t){ clearTimeout(t); } t = setTimeout(apply, 120); }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ apply(); });
  } else { apply(); }
  window.addEventListener('resize', onResize);
})();

/* ===== 全站隐私勾选校验（.hsst-consent，invalid 事件方案）=====
   依赖 HTML5 required 原生拦截提交；在浏览器派发 invalid 事件时，
   给未勾选的复选框加红框 + 显示内联红字提示（保留浏览器气泡）。 */
(function(){
  function tip(lang){
    return (lang && lang.indexOf('zh') === 0) ? '請勾選同意隱私政策' : 'Please check the box to agree to the Privacy Policy.';
  }
  function bind(){
    var lang = document.documentElement.lang || '';
    var msg = tip(lang);
    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) {
      var form = forms[i];
      if (form.getAttribute('data-hsst-consent')) continue;
      form.setAttribute('data-hsst-consent', '1');
      var boxes = form.querySelectorAll('.hsst-consent input[type="checkbox"][required]');
      for (var j = 0; j < boxes.length; j++) {
        (function(cb){
          var label = cb.closest('.hsst-consent');
          if (!label) return;
          var err = label.nextElementSibling;
          if (!err || !err.classList || !err.classList.contains('hsst-consent-error')) {
            err = document.createElement('span');
            err.className = 'hsst-consent-error';
            err.textContent = msg;
            label.insertAdjacentElement('afterend', err);
          }
          cb.addEventListener('invalid', function(){
            cb.classList.add('error');
            if (err) err.classList.add('show');
          });
          cb.addEventListener('change', function(){
            cb.classList.remove('error');
            if (err) err.classList.remove('show');
          });
          cb.addEventListener('blur', function(){
            if (cb.checked) { cb.classList.remove('error'); if (err) err.classList.remove('show'); }
          });
        })(boxes[j]);
      }
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else { bind(); }
})();

/* ===== PWA：仅保留 ServiceWorker 注册 =====
   2026-09-08：按要求移除「添加到桌面/Add to Desktop」悬浮按钮与指引弹窗（全站中英）。
   SW 注册保留，离线缓存与浏览器原生安装入口不受影响。 */
(function(){
  if ('serviceWorker' in navigator) {
    try { navigator.serviceWorker.register('/sw.js'); } catch(e) {}
  }
})();

/* ── 导航高亮（全局，基于路径判断，2026-09-06）────────────────
   修复: 高亮与当前页面所属栏目不一致 / 多重高亮。
   规则: 目录优先(news/products/projects/solutions/technology/about)，
         其次按文件名映射；先清除全部顶级 active 再标记唯一正确项。 */
(function () {
  var segs = window.location.pathname.split('/').filter(Boolean);
  var file = segs.length ? segs[segs.length - 1] : 'index.html';
  var dir = segs.length >= 2 ? segs[segs.length - 2] : '';
  var DIR_GROUP = { products: 'products', projects: 'projects', news: 'news', solutions: 'solutions', technology: 'about', about: 'about' };
  var FILE_GROUP = {
    'index.html': 'home', 'about.html': 'about', 'honors.html': 'about', 'careers.html': 'about',
    'partnerships.html': 'about', 'technology.html': 'about',
    'products.html': 'products', 'manufacturing.html': 'products', 'mines.html': 'products',
    'projects.html': 'projects', 'news.html': 'news', 'resources.html': 'news', 'faq.html': 'news',
    'solutions.html': 'solutions', 'contact.html': 'contact'
  };
  function groupOf(dirName, fileName) {
    return DIR_GROUP[dirName] || FILE_GROUP[fileName] || (fileName === 'index.html' ? 'home' : null);
  }
  var group = groupOf(dir, file);
  if (!group) return;

  var topLinks = document.querySelectorAll('.navbar .nav-links > a, .navbar .nav-dropdown > a');
  Array.prototype.forEach.call(topLinks, function (a) {
    if (a.closest('.lang-switch')) return;
    a.classList.remove('active');
  });
  Array.prototype.forEach.call(topLinks, function (a) {
    var href = a.getAttribute('href') || '';
    var parts = href.split('/').filter(Boolean);
    var hf = parts.length ? parts[parts.length - 1] : 'index.html';
    var hd = parts.length >= 2 ? parts[parts.length - 2] : '';
    if (groupOf(hd, hf) === group) a.classList.add('active');
  });

  // 二级子菜单(mega-panel-link): 当前页对应条目高亮
  var panelLinks = document.querySelectorAll('.mega-panel-link');
  Array.prototype.forEach.call(panelLinks, function (a) {
    var href = a.getAttribute('href') || '';
    var parts = href.split('/').filter(Boolean);
    var pf = parts.length ? parts[parts.length - 1] : 'index.html';
    var pd = parts.length >= 2 ? parts[parts.length - 2] : '';
    if (pf === file && groupOf(pd, pf) === group) a.classList.add('active');
  });
})();
