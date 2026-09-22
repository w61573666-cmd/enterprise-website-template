/* ============================================================
   HENGSHENG MARBLE — Stone Comparison System v2.0
   ------------------------------------------------------------
   v2 變更：
   - 唯一識別改為「品類/slug」，解決跨品類重名（black-galaxy / amazon-green / calacatta-gold）
   - 對比表改用全站統一參數數據源 js/product-specs.js（window.HSST_SPECS）
   - 統一參數維度逐行對齊；缺失項顯示「不支援／無 / Not applicable」
   - 差異項自動高亮，可切換「只顯示差異」
   - 支援 a.v2-series-card.ev-card 卡片（工程石製品 / 工程專供）
   - 行動端：參數名欄固定，表格橫向捲動
   [CRITICAL CODE - DO NOT DELETE OR MODIFY]
   ============================================================ */
(function () {
  'use strict';
  if (window.__HSST_COMPARE_LOADED__) return;
  window.__HSST_COMPARE_LOADED__ = true;

  var STORAGE_KEY = 'hsst_compare_items_v2';
  var MAX_ITEMS = 6;
  var LANG = (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0 ? 'en' : 'zh';

  // ---- 文本 ----
  var I18N = {
    zh: {
      add: '加入比較', added: '✓ 已加入', remove: '取消',
      drawerTitle: '已選品種', drawerSub: '點擊「立即比較」開始對比',
      compareNow: '立即比較', clearAll: '全部清除',
      empty: '尚未選取任何品種', maxTip: '最多可選 6 個品種',
      pageTitle: '品種對比', pageSub: '按全站統一參數維度逐行對齊，差異項自動高亮',
      thumbCol: '代表圖', nameCol: '名稱', catCol: '所屬品類',
      backBtn: '← 返回上一頁', cleared: '已清除全部',
      addedToast: '已加入比較', removedToast: '已從比較中移除',
      maxToast: '最多只能選 6 個品種',
      diffOnly: '只顯示差異項', allFields: '顯示全部參數',
      diffBadge: '差異', legend: '參數說明',
      noData: '參數數據未載入', naTitle: '不支援／無',
      unit: '單位'
    },
    en: {
      add: 'Add to Compare', added: '✓ Added', remove: 'Remove',
      drawerTitle: 'Selected Stones', drawerSub: 'Click "Compare Now" to compare',
      compareNow: 'Compare Now', clearAll: 'Clear All',
      empty: 'No stones selected yet', maxTip: 'Up to 6 stones',
      pageTitle: 'Stone Comparison', pageSub: 'Unified parameter rows, differences highlighted',
      thumbCol: 'Image', nameCol: 'Name', catCol: 'Category',
      backBtn: '← Back', cleared: 'All cleared',
      addedToast: 'Added to compare', removedToast: 'Removed from compare',
      maxToast: 'You can compare up to 6 stones',
      diffOnly: 'Differences only', allFields: 'Show all parameters',
      diffBadge: 'DIFF', legend: 'Legend',
      noData: 'Specification data not loaded', naTitle: 'Not applicable',
      unit: 'Unit'
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
    try { window.dispatchEvent(new CustomEvent('hsst:compare-changed')); } catch (e) {}
  }
  function escapeHTML(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c];
    });
  }
  function resolveUrl(url) {
    if (!url) return '';
    if (/^https?:\/\//.test(url) || url.indexOf('data:') === 0) return url;
    var a = document.createElement('a');
    a.href = url;
    return a.href;
  }
  function specs() { return window.HSST_SPECS || null; }

  // 由路徑推導「品類/slug」
  function catFromPath() {
    var m = location.pathname.match(/\/products\/([^\/]+)\/([^\/]+)\.html/);
    if (m) return m[1];
    m = location.pathname.match(/\/products\/([^\/]+)\.html/);
    return m ? m[1] : '';
  }
  function idFromHref(href) {
    var m = String(href || '').match(/\/products\/([^\/]+)\/([^\/]+)\.html/);
    if (m) return m[1] + '/' + m[2].replace(/\.html$/, '');
    return '';
  }

  // 品類名稱
  function catName(cat) {
    var S = specs();
    if (!S) return cat;
    return LANG === 'en' ? (S.CAT_EN && S.CAT_EN[cat]) || cat : (S.CAT_ZH && S.CAT_ZH[cat]) || cat;
  }

  // ---- 頁面類型判定 ----
  function hasVarietyCards() {
    return !!document.querySelector('article.eng-var[id]');
  }
  function hasSeriesCards() {
    return !!document.querySelector('a.v2-series-card.ev-card[href]');
  }
  function isVarietyDetail() {
    return !!document.querySelector('.eng-var-page-body, .eng-variety-grid');
  }
  function pageHasVariety() {
    if (document.body.classList.contains('hsst-compare-page')) return false;
    return hasVarietyCards() || hasSeriesCards() || isVarietyDetail();
  }

  // ---- 浮動抽屜 ----
  function ensureTray() {
    var tray = document.getElementById('hsst-cmp-tray');
    if (tray) return tray;
    if (document.body.classList.contains('hsst-compare-page')) return null;
    var hasStored = false;
    try { hasStored = (JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]').length > 0); } catch (e) {}
    if (!pageHasVariety() && !hasStored) return null;
    tray = document.createElement('div');
    tray.id = 'hsst-cmp-tray';
    tray.className = 'hsst-cmp-tray';
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
    syncButtons(items);
  }

  function bindTray() {
    var tray = ensureTray();
    if (!tray) return;
    var handle = tray.querySelector('.hsst-cmp-handle');
    var panel = tray.querySelector('.hsst-cmp-panel');
    handle.addEventListener('click', function () {
      var open = !panel.hasAttribute('hidden');
      if (open) { panel.setAttribute('hidden', ''); handle.setAttribute('aria-expanded', 'false'); }
      else { panel.removeAttribute('hidden'); handle.setAttribute('aria-expanded', 'true'); }
    });
    tray.querySelector('.hsst-cmp-clear').addEventListener('click', function () {
      write([]);
      toast(T.cleared);
    });
    tray.querySelector('.hsst-cmp-list').addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('.hsst-cmp-item-x') : null;
      if (!btn) return;
      var idx = parseInt(btn.getAttribute('data-idx'), 10);
      var items = read();
      items.splice(idx, 1);
      write(items);
    });
  }

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

  // ---- 注入按鈕 ----
  function makeBtn(item, extraClass) {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'hsst-cmp-cta' + (extraClass ? ' ' + extraClass : '');
    btn.setAttribute('data-cmp-id', item.id);
    btn.setAttribute('aria-label', T.add);
    btn.innerHTML = '<span class="hsst-cmp-btn-label">' + escapeHTML(T.add) + '</span>';
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggleItem(item, btn);
    });
    return btn;
  }

  // A. article.eng-var[id] 卡片（白雲石／花崗巖／人造石…）
  function injectToCards() {
    var cat = catFromPath();
    Array.prototype.forEach.call(document.querySelectorAll('article.eng-var[id]'), function (card) {
      if (card.querySelector(':scope > .hsst-cmp-cta')) return;
      var slug = card.id;
      if (!slug) return;
      var h3 = card.querySelector('h3');
      if (!h3) return;
      var nameNodes = Array.prototype.filter.call(h3.childNodes, function (n) {
        return n.nodeType === 3 || (n.nodeType === 1 && !(n.classList && (n.classList.contains('eng-var-name-en') || n.classList.contains('eng-var-idx'))));
      });
      var name = nameNodes.map(function (n) { return n.textContent.trim(); }).join(' ').replace(/\s+/g, ' ').trim();
      var enNode = h3.querySelector('.eng-var-name-en');
      var img = card.querySelector('img');
      var link = card.querySelector('a');
      var item = {
        id: cat + '/' + slug,
        name: name,
        en: enNode ? enNode.textContent.trim() : '',
        image: img ? (img.currentSrc || img.src) : '',
        link: link ? link.href : '',
        cat: cat
      };
      card.appendChild(makeBtn(item));
    });
  }

  // B. a.v2-series-card.ev-card 卡片（工程石製品 / 工程專供）
  function injectToSeriesCards() {
    var cat = catFromPath();
    Array.prototype.forEach.call(document.querySelectorAll('a.v2-series-card.ev-card[href]'), function (card) {
      if (card.querySelector('.hsst-cmp-cta')) return;
      // 用 card.href（瀏覽器解析後的絕對網址），避免相對路徑 href 解析失敗
      var id = idFromHref(card.href) || idFromHref(card.getAttribute('href'));
      if (!id) return;
      var b = card.querySelector('.vsc-cap b');
      var i = card.querySelector('.vsc-cap i');
      var img = card.querySelector('img');
      var item = {
        id: id,
        name: b ? b.textContent.trim() : id.split('/')[1],
        en: i ? i.textContent.trim() : '',
        image: img ? (img.currentSrc || img.src) : '',
        link: card.href,
        cat: id.split('/')[0]
      };
      card.appendChild(makeBtn(item, 'hsst-cmp-cta-inline'));
    });
  }

  // C. 品種詳情頁
  function injectToDetail() {
    if (document.querySelector('.hsst-cmp-cta[data-cmp-detail]')) return;
    if (!isVarietyDetail()) return;
    var h1 = document.querySelector('.product-hero-title') || document.querySelector('h1');
    if (!h1) return;
    var id = catFromPath();
    var m = location.pathname.match(/\/products\/([^\/]+)\/([^\/]+)\.html/);
    if (!m) return;
    id = m[1] + '/' + m[2];
    var mainImg = document.querySelector('img.product-hero-bg, .product-hero img, .eng-variety-grid img, picture img');
    var sub = document.querySelector('.product-hero-subtitle');
    var item = {
      id: id,
      name: (h1.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80),
      en: sub ? (sub.textContent || '').trim().slice(0, 80) : '',
      image: mainImg ? (mainImg.currentSrc || mainImg.src) : '',
      link: location.href,
      cat: m[1]
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
    var bar = document.querySelector('.product-action-bar .container, .product-action-bar');
    if (bar) bar.appendChild(btn);
    else h1.insertAdjacentElement('afterend', btn);
  }

  function toggleItem(item, btn) {
    var items = read();
    var idx = -1;
    for (var i = 0; i < items.length; i++) { if (items[i].id === item.id) { idx = i; break; } }
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

  // ---- 對比頁渲染（統一參數維度）----
  function renderComparePage() {
    if (!document.body.classList.contains('hsst-compare-page')) return;
    var wrap = document.getElementById('hsst-cmp-grid');
    if (!wrap) return;
    var items = read();
    if (!items.length) {
      wrap.className = 'hsst-cmp-empty-page';
      wrap.innerHTML = '<p>' + escapeHTML(T.empty) + '</p>';
      return;
    }
    var S = specs();
    if (!S) {
      wrap.className = '';
      wrap.innerHTML = '<p class="hsst-cmp-nodata">' + escapeHTML(T.noData) + '</p>';
      return;
    }

    var cols = items.length;
    var MISSING = S.pick(S.MISSING, LANG);
    var html = '';

    // 工具列
    html += '<div class="hsst-cmp-toolbar">';
    html += '<label class="hsst-cmp-toggle"><input type="checkbox" id="hsst-cmp-diffonly"><span>' + escapeHTML(T.diffOnly) + '</span></label>';
    html += '<span class="hsst-cmp-legend">' + escapeHTML(T.legend) + '：<i class="hsst-cmp-swatch hsst-cmp-swatch-diff"></i>' + escapeHTML(T.diffBadge) + '</span>';
    html += '</div>';

    html += '<div class="hsst-cmp-table" style="--cols:' + cols + '">';

    // 表頭
    html += '<div class="hsst-cmp-row hsst-cmp-head">';
    html += '<div class="hsst-cmp-cell hsst-cmp-th hsst-cmp-label">' + escapeHTML(T.nameCol) + '</div>';
    items.forEach(function (it) {
      html += '<div class="hsst-cmp-cell hsst-cmp-th">';
      html += '<img alt="" src="' + escapeHTML(resolveUrl(it.image)) + '">';
      html += '<div class="hsst-cmp-name">' + escapeHTML(it.name) + '</div>';
      if (it.en) html += '<div class="hsst-cmp-en">' + escapeHTML(it.en) + '</div>';
      html += '<button class="hsst-cmp-remove" data-id="' + escapeHTML(it.id) + '" type="button">' + escapeHTML(T.remove) + '</button>';
      html += '</div>';
    });
    html += '</div>';

    // 所屬品類
    html += '<div class="hsst-cmp-row">';
    html += '<div class="hsst-cmp-cell hsst-cmp-label">' + escapeHTML(T.catCol) + '</div>';
    items.forEach(function (it) {
      html += '<div class="hsst-cmp-cell">' + escapeHTML(catName(it.cat || (it.id || '').split('/')[0])) + '</div>';
    });
    html += '</div>';

    // 統一參數維度（逐行對齊）
    var groups = S.GROUPS || [];
    var fields = S.FIELDS || [];
    groups.forEach(function (g) {
      var gf = fields.filter(function (f) { return f.group === g.key; });
      if (!gf.length) return;
      // 該組若全部產品皆缺失則整組略過
      var anyValue = gf.some(function (f) {
        return items.some(function (it) { return S.getSpec(it.id) && (S.getSpec(it.id).values[f.key] != null); });
      });
      if (!anyValue) return;
      html += '<div class="hsst-cmp-row hsst-cmp-grouprow"><div class="hsst-cmp-cell hsst-cmp-group">' + escapeHTML(S.pick(g.name, LANG)) + '</div></div>';
      gf.forEach(function (f) {
        var vals = items.map(function (it) { return S.getField(it.id, f.key, LANG); });
        var present = vals.filter(function (v) { return v !== MISSING; });
        if (!present.length) return;                       // 全缺 → 整行略過
        var first = present[0];
        var isDiff = present.some(function (v) { return v !== first; });
        html += '<div class="hsst-cmp-row hsst-cmp-fieldrow' + (isDiff ? ' is-diff' : '') + '">';
        var label = S.pick(f.name, LANG);
        if (f.unit) label += '（' + f.unit + '）';
        html += '<div class="hsst-cmp-cell hsst-cmp-label">' + escapeHTML(label) +
                (isDiff ? '<span class="hsst-cmp-diffbadge">' + escapeHTML(T.diffBadge) + '</span>' : '') + '</div>';
        vals.forEach(function (v) {
          if (v === MISSING) {
            html += '<div class="hsst-cmp-cell is-na" title="' + escapeHTML(T.naTitle) + '">' + escapeHTML(MISSING) + '</div>';
          } else {
            var cls = (isDiff && v !== first) ? ' is-diffcell' : '';
            html += '<div class="hsst-cmp-cell' + cls + '">' + escapeHTML(v) + '</div>';
          }
        });
        html += '</div>';
      });
    });

    html += '</div>';
    wrap.className = 'hsst-cmp-wrap';
    wrap.innerHTML = html;

    // 「只顯示差異」
    var cb = document.getElementById('hsst-cmp-diffonly');
    if (cb) {
      cb.addEventListener('change', function () {
        wrap.classList.toggle('only-diff', cb.checked);
      });
    }
    // 移除
    Array.prototype.forEach.call(wrap.querySelectorAll('.hsst-cmp-remove'), function (b) {
      b.addEventListener('click', function () {
        var id = b.getAttribute('data-id');
        write(read().filter(function (i) { return i.id !== id; }));
        renderComparePage();
      });
    });
  }

  // ---- init ----
  function init() {
    bindTray();
    injectToCards();
    injectToSeriesCards();
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
