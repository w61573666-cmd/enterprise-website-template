/* ============================================================
   HENGSHENG MARBLE — Stone Comparison System v1.0
   - 自动为品种卡片（.eng-var）注入「+ 加入比較」按钮
   - 自动为品种详情页注入「加入比較」按钮（基于页面 H1 + 主图）
   - localStorage 持久化（最多 6 个）
   - 全站右下角浮动抽屉
   - /compare.html 渲染对比表
   ============================================================ */
(function () {
  'use strict';
  if (window.__HSST_COMPARE_LOADED__) return;
  window.__HSST_COMPARE_LOADED__ = true;

  var STORAGE_KEY = 'hsst_compare_items_v1';
  var MAX_ITEMS = 6;
  var LANG = (document.documentElement.lang || '').toLowerCase().startsWith('en') ? 'en' : 'zh';

  // ---- 文本 ----
  var I18N = {
    zh: {
      add: '加入比較',
      added: '✓ 已加入',
      remove: '取消',
      drawerTitle: '已選品種',
      drawerSub: '點擊「立即比較」開始對比',
      compareNow: '立即比較',
      clearAll: '全部清除',
      empty: '尚未選取任何品種',
      maxTip: '最多可選 ' + MAX_ITEMS + ' 個品種',
      pageTitle: '品種對比',
      pageSub: '並排查看多個品種的紋理、應用與規格',
      thumbCol: '代表圖',
      nameCol: '名稱',
      originCol: '產地 / 系列',
      appCol: '推薦應用',
      specCol: '規格',
      backBtn: '← 返回上一頁',
      cleared: '已清除全部',
      addedToast: '已加入比較',
      removedToast: '已從比較中移除',
      maxToast: '最多只能選 ' + MAX_ITEMS + ' 個品種'
    },
    en: {
      add: 'Add to Compare',
      added: '✓ Added',
      remove: 'Remove',
      drawerTitle: 'Selected Stones',
      drawerSub: 'Click "Compare Now" to compare',
      compareNow: 'Compare Now',
      clearAll: 'Clear All',
      empty: 'No stones selected yet',
      maxTip: 'Up to ' + MAX_ITEMS + ' stones',
      pageTitle: 'Stone Comparison',
      pageSub: 'Compare texture, application and spec side-by-side',
      thumbCol: 'Image',
      nameCol: 'Name',
      originCol: 'Origin / Series',
      appCol: 'Application',
      specCol: 'Specification',
      backBtn: '← Back',
      cleared: 'All cleared',
      addedToast: 'Added to compare',
      removedToast: 'Removed from compare',
      maxToast: 'You can compare up to ' + MAX_ITEMS + ' stones'
    }
  };
  var T = I18N[LANG];

  // ---- 工具 ----
  function read() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
    catch (e) { return []; }
  }
  function write(arr) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(arr)); } catch (e) {}
    window.dispatchEvent(new CustomEvent('hsst:compare-changed'));
  }
  function escapeHTML(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function resolveUrl(url) {
    if (!url) return '';
    if (/^https?:\/\//.test(url) || url.startsWith('data:')) return url;
    var a = document.createElement('a');
    a.href = url;
    return a.href;
  }

  // ---- 页面类型判定 ----
  // 站内只有两类页面存在「可对比的品种」，其余页面（首页 / 关于 / 联络 / 资讯 /
  // 工程案例 / 招聘 / 技术 …）一律不出任何对比入口，避免「没有对比对象却有对比按钮」。
  //   A. 品种落地页：含 article.eng-var[id] 卡片 → 每张卡片一个按钮
  //   B. 品种详情页：含 .eng-var-page-body / .eng-variety-grid → 页级一个按钮
  function hasVarietyCards() {
    return !!document.querySelector('article.eng-var[id]');
  }
  function isVarietyDetail() {
    return !!document.querySelector('.eng-var-page-body, .eng-variety-grid');
  }
  function pageHasVariety() {
    if (document.body.classList.contains('hsst-compare-page')) return false;
    return hasVarietyCards() || isVarietyDetail();
  }

  function ensureTray() {
    var tray = document.getElementById('hsst-cmp-tray');
    if (tray) return tray;
    // 对比页本身即对比视图，不再叠加浮动抽屉
    if (document.body.classList.contains('hsst-compare-page')) return null;
    // 没有可对比品种 AND localStorage 也无数据 — 不创建（避免空抽屉干扰）
    var hasStored = false;
    try { hasStored = (JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]').length > 0); } catch(e) {}
    if (!pageHasVariety() && !hasStored) return null;
    tray = document.createElement('div');
    tray.id = 'hsst-cmp-tray';
    tray.className = 'hsst-cmp-tray';
    // 默认 display:none — 有项目时才显示
    tray.style.display = 'none';
    tray.innerHTML = [
      '<button class="hsst-cmp-handle" aria-label="' + escapeHTML(T.drawerTitle) + '" aria-expanded="false">',
      '  <span class="hsst-cmp-icon" aria-hidden="true">⚖️</span>',
      '  <span class="hsst-cmp-count">0</span>',
      '</button>',
      '<div class="hsst-cmp-panel" hidden>',
      '  <div class="hsst-cmp-panel-head">',
      '    <h3>' + escapeHTML(T.drawerTitle) + '</h3>',
      '    <button class="hsst-cmp-clear" type="button">' + escapeHTML(T.clearAll) + '</button>',
      '  </div>',
      '  <p class="hsst-cmp-sub">' + escapeHTML(T.drawerSub) + '</p>',
      '  <div class="hsst-cmp-list"></div>',
      '  <div class="hsst-cmp-actions"><a class="hsst-cmp-go" href="' + (LANG === 'en' ? '/en/compare.html' : '/compare.html') + '">' + escapeHTML(T.compareNow) + '</a></div>',
      '  <p class="hsst-cmp-tip">' + escapeHTML(T.maxTip) + '</p>',
      '</div>'
    ].join('');
    document.body.appendChild(tray);
    return tray;
  }

  // 同步页内所有对比按钮的选中态（抽屉是否显示都要同步，否则取消后会残留「已加入」）
  function syncButtons(items) {
    Array.prototype.forEach.call(document.querySelectorAll('[data-cmp-id]'), function (btn) {
      var id = btn.getAttribute('data-cmp-id');
      var hit = items.some(function (i) { return i.id === id; });
      btn.classList.toggle('cmp-selected', hit);
      btn.setAttribute('aria-pressed', hit ? 'true' : 'false');
      var lbl = btn.querySelector('.hsst-cmp-btn-label');
      if (lbl) lbl.textContent = hit ? T.added : T.add;
    });
  }

  function renderTray() {
    var items = read();
    var tray = document.getElementById('hsst-cmp-tray');
    if (tray) {
      if (items.length === 0) {
        // 空状态：彻底隐藏抽屉（首页等无品种页不显示，跨页持久但不出现在无关页）
        tray.style.display = 'none';
      } else {
        tray.style.display = '';
        tray.querySelector('.hsst-cmp-count').textContent = String(items.length);
        var list = tray.querySelector('.hsst-cmp-list');
        list.innerHTML = items.map(function (it, idx) {
          return [
            '<div class="hsst-cmp-item" data-id="' + escapeHTML(it.id) + '">',
            '  <img alt="" loading="lazy" src="' + escapeHTML(resolveUrl(it.image)) + '">',
            '  <div class="hsst-cmp-item-meta">',
            '    <div class="hsst-cmp-item-name">' + escapeHTML(it.name) + '</div>',
            (it.en ? '<div class="hsst-cmp-item-en">' + escapeHTML(it.en) + '</div>' : ''),
            '  </div>',
            '  <button class="hsst-cmp-item-x" type="button" aria-label="' + escapeHTML(T.remove) + '" data-idx="' + idx + '">×</button>',
            '</div>'
          ].join('');
        }).join('');
      }
    }
    // 页内按钮状态始终同步（含取消到 0 个的情况），否则会残留「✓ 已加入」
    syncButtons(items);
  }

  function bindTray() {
    var tray = ensureTray();
    if (!tray) return; // 没有可对比品种的页面 — 不绑定
    var handle = tray.querySelector('.hsst-cmp-handle');
    var panel = tray.querySelector('.hsst-cmp-panel');
    handle.addEventListener('click', function () {
      var open = !panel.hasAttribute('hidden');
      if (open) {
        panel.setAttribute('hidden', '');
        handle.setAttribute('aria-expanded', 'false');
      } else {
        panel.removeAttribute('hidden');
        handle.setAttribute('aria-expanded', 'true');
      }
    });
    tray.querySelector('.hsst-cmp-clear').addEventListener('click', function () {
      write([]);
      toast(T.cleared);
    });
    tray.querySelector('.hsst-cmp-list').addEventListener('click', function (e) {
      var btn = e.target.closest('.hsst-cmp-item-x');
      if (!btn) return;
      var idx = parseInt(btn.getAttribute('data-idx'), 10);
      var items = read();
      items.splice(idx, 1);
      write(items);
    });
  }

  // ---- toast ----
  function toast(msg) {
    var t = document.getElementById('hsst-cmp-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'hsst-cmp-toast';
      t.className = 'hsst-cmp-toast';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    t.classList.add('show');
    clearTimeout(t.__timer);
    t.__timer = setTimeout(function () { t.classList.remove('show'); }, 1800);
  }

  // ---- 注入按钮到卡片 ----
  function injectToCard(card) {
    if (!card || card.querySelector(':scope > .hsst-cmp-cta')) return;
    var id = card.id || (card.getAttribute('data-cmp-id') || '');
    if (!id) return;
    var h3 = card.querySelector('h3');
    if (!h3) return;
    // 抓取名称：去掉序号 prefix（"01"）和英文 span
    var nameNodes = Array.prototype.filter.call(h3.childNodes, function (n) {
      return n.nodeType === 3 || (n.nodeType === 1 && !n.classList.contains('eng-var-name-en') && !n.classList.contains('eng-var-idx'));
    });
    var name = nameNodes.map(function (n) { return n.textContent.trim(); }).join(' ').replace(/\s+/g, ' ').trim();
    var enNode = h3.querySelector('.eng-var-name-en');
    var enName = enNode ? enNode.textContent.trim() : '';
    var img = card.querySelector('img');
    var link = card.querySelector('a');
    var item = {
      id: id,
      name: name,
      en: enName,
      image: img ? (img.currentSrc || img.src) : '',
      link: link ? link.href : '',
      origin: (LANG === 'en' ? 'Stone Collection' : '石材系列'),
      application: '',
      spec: ''
    };

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hsst-cmp-cta';
    btn.setAttribute('data-cmp-id', id);
    btn.setAttribute('aria-label', T.add);
    btn.innerHTML = '<span class="hsst-cmp-btn-label">' + escapeHTML(T.add) + '</span>';
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleItem(item, btn);
    });
    card.appendChild(btn);
  }

  // ---- 注入按钮到品种详情页 ----
  function injectToDetail() {
    // 已经注入过的不要重复
    if (document.querySelector('.hsst-cmp-cta[data-cmp-detail]')) return;
    // 只有品种详情页才注入 —— 首页/关于/联络等页面没有可对比对象，绝不出现按钮
    if (!isVarietyDetail()) return;
    var h1 = document.querySelector('.product-hero-title') || document.querySelector('h1');
    if (!h1) return;
    var id = (location.pathname.split('/').pop() || '').replace('.html', '');
    if (!id || id === 'index') return;
    // 代表图：优先该品种专属 hero 图，退回第一个样本图
    var mainImg = document.querySelector('img.product-hero-bg, .product-hero img, .eng-variety-grid img, picture img');
    var sub = document.querySelector('.product-hero-subtitle');
    var badge = document.querySelector('.product-hero-badge');
    var name = (h1.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80);
    var item = {
      id: id,
      name: name,
      en: sub ? (sub.textContent || '').trim().slice(0, 80) : '',
      image: mainImg ? (mainImg.currentSrc || mainImg.src) : '',
      link: location.href,
      origin: badge ? (badge.textContent || '').trim() : '',
      application: '',
      spec: ''
    };
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hsst-cmp-cta hsst-cmp-cta-detail';
    btn.setAttribute('data-cmp-id', id);
    btn.setAttribute('data-cmp-detail', '1');
    btn.setAttribute('aria-label', T.add);
    btn.innerHTML = '<span class="hsst-cmp-btn-icon" aria-hidden="true">⚖️</span><span class="hsst-cmp-btn-label">' + escapeHTML(T.add) + '</span>';
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleItem(item, btn);
    });
    // 插入位置：优先与「索取樣板 / 立即諮詢」并列，退回 H1 之后
    var bar = document.querySelector('.product-action-bar .container, .product-action-bar');
    if (bar) {
      bar.appendChild(btn);
    } else {
      h1.insertAdjacentElement('afterend', btn);
    }
  }

  // ---- 切换加入/取消 ----
  function toggleItem(item, btn) {
    var items = read();
    var idx = items.findIndex(function (i) { return i.id === item.id; });
    if (idx >= 0) {
      items.splice(idx, 1);
      write(items);
      toast(T.removedToast);
    } else {
      if (items.length >= MAX_ITEMS) {
        toast(T.maxToast);
        if (btn) {
          btn.classList.add('hsst-cmp-shake');
          setTimeout(function () { btn.classList.remove('hsst-cmp-shake'); }, 400);
        }
        return;
      }
      items.push(item);
      write(items);
      toast(T.addedToast);
    }
  }

  // ---- 对比页渲染 ----
  function renderComparePage() {
    if (!document.body.classList.contains('hsst-compare-page')) return;
    var items = read();
    var wrap = document.getElementById('hsst-cmp-grid');
    if (!wrap) return;
    if (!items.length) {
      wrap.innerHTML = '<div class="hsst-cmp-empty-page"><p>' + escapeHTML(T.empty) + '</p></div>';
      return;
    }
    var cols = items.length;
    var html = '<div class="hsst-cmp-table" style="--cols:' + cols + '">';
    html += '<div class="hsst-cmp-row hsst-cmp-head">';
    html += '<div class="hsst-cmp-cell hsst-cmp-th"></div>';
    items.forEach(function (it) {
      html += '<div class="hsst-cmp-cell hsst-cmp-th">';
      html += '<img alt="" src="' + escapeHTML(resolveUrl(it.image)) + '">';
      html += '<div class="hsst-cmp-name">' + escapeHTML(it.name) + '</div>';
      if (it.en) html += '<div class="hsst-cmp-en">' + escapeHTML(it.en) + '</div>';
      html += '<button class="hsst-cmp-remove" data-id="' + escapeHTML(it.id) + '" type="button">' + escapeHTML(T.remove) + '</button>';
      html += '</div>';
    });
    html += '</div>';
    ['origin', 'application', 'spec'].forEach(function (key) {
      var labelKey = key === 'origin' ? 'originCol' : (key === 'application' ? 'appCol' : 'specCol');
      html += '<div class="hsst-cmp-row">';
      html += '<div class="hsst-cmp-cell hsst-cmp-label">' + escapeHTML(T[labelKey]) + '</div>';
      items.forEach(function (it) {
        html += '<div class="hsst-cmp-cell">' + escapeHTML(it[key] || '—') + '</div>';
      });
      html += '</div>';
    });
    html += '</div>';
    wrap.innerHTML = html;
    wrap.querySelectorAll('.hsst-cmp-remove').forEach(function (b) {
      b.addEventListener('click', function () {
        var id = b.getAttribute('data-id');
        var items2 = read().filter(function (i) { return i.id !== id; });
        write(items2);
        renderComparePage();
      });
    });
  }

  // ---- init ----
  function init() {
    bindTray();
    // 先注入页内按钮，再渲染抽屉 — 保证按钮能同步「已加入」状态
    Array.prototype.forEach.call(document.querySelectorAll('article.eng-var[id]'), injectToCard);
    injectToDetail();
    renderTray();
    renderComparePage();
    window.addEventListener('hsst:compare-changed', function () {
      renderTray();
      renderComparePage();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();