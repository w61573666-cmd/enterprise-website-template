/* =================================================================
   [CRITICAL CODE - DO NOT DELETE OR MODIFY / 核心代碼 嚴禁刪除]
   HSST 全站表單「來源頁面採集器」（Form Source Collector）
   -----------------------------------------------------------------
   PURPOSE : 每個提交到 splitforms 的通知郵件，自動帶上訪客當時瀏覽的
             ① 來源頁面（層級 / 麵包屑格式，如「首頁 / 產品中心 - 精品麻石」）
             ② 頁面連結（完整 https 網址，含路徑與參數）
             ③ 表單實例標識 form_id（穩定唯一，精準點名「具體哪個表單」）
             ④ 來源摘要（自帶中/英文標籤的獨立區塊，含上述三項）
             ⑤ 郵件主旨尾綴「來源：XXX」
   HOW IT WORKS:
     · 頁面 HTML 內已靜態內建 source_page / page_url / source_details
       三個 hidden 欄位（伺服器端即可生效，禁用 JS 也能送出基本來源）
     · 本檔在執行時「覆寫更新」這三個欄位的值：網址一律改用瀏覽器當下
       真實的 location.href（含 query string），來源層級重新以頁面
       JSON-LD BreadcrumbList 計算 → 因此「彈窗 / 共用頁首 / 頁尾」等
       全域表單在任一頁面都能記錄到訪客真正的所在頁。
     · 同時監聽 ① DOMContentLoaded ② 送出前的捕獲階段 ③ DOM 動態新增表單
       (MutationObserver) ④ 焦點進入表單 — 四個時機均可補寫，確保不漏。
   WARNING: 欄位名稱必須保持 ASCII（multipart/form-data 對非 ASCII
            欄位名相容性極差）；主旨尾綴會保留原有 _subject 前置標籤。
   ================================================================= */
(function () {
  "use strict";
  if (window.__HSST_FORM_SOURCE__) return;
  window.__HSST_FORM_SOURCE__ = true;

  var LANG = (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0 ? 'en' : 'zh';
  var T = function (en, zh) { return LANG === 'en' ? en : zh; };

  /* ---------------- 來源層級（麵包屑）計算 ---------------- */

  /* 去掉品牌贅尾：恆生石材 / HSST / Hong Kong 等後綴 */
  var BRAND_TAIL = /^(?:[A-Za-z0-9\s&,'\.]*(?:Hong\s*Kong|Hengsheng|Heng\s*Sang|marble\s*supplier|stone\s*supplier|granite\s*supplier|marble\s*Hong\s*Kong)[A-Za-z0-9\s&,'\.]*)$/i;
  function stripBrand(name) {
    if (!name) return name;
    var s = String(name)
      .replace(/\s*[|｜]\s*(?:[^|｜]*(?:恆生石材|恒生石材|HSST|Hang\s*Sang)[^|｜]*)\s*$/i, '')
      .trim();
    /* 英文頁常見 SEO 贅尾：「Core Strengths — Hong Kong marble supplier」 */
    s = s.replace(/\s+[—–]\s+([^—–]{2,52})$/, function (m, tail) {
      if (/[\u4e00-\u9fff]/.test(tail)) return m;      /* 含中文 → 視為正式標題的一部分 */
      return BRAND_TAIL.test(tail.trim()) ? '' : m;
    }).trim();
    return s;
  }

  function fromJsonLd() {
    var found = null;
    var nodes = document.querySelectorAll('script[type="application/ld+json"]');
    for (var i = 0; i < nodes.length; i++) {
      var raw = (nodes[i].textContent || '').trim();
      if (raw.indexOf('BreadcrumbList') < 0) continue;
      var data;
      try { data = JSON.parse(raw); } catch (e) { try { data = JSON.parse(raw.replace(/[\r\n]+/g, ' ')); } catch (e2) { continue; } }
      var list = null;
      (function walk(o) {
        if (list) return;
        if (Object.prototype.toString.call(o) === '[object Array]') {
          for (var k = 0; k < o.length; k++) walk(o[k]);
          return;
        }
        if (!o || typeof o !== 'object') return;
        var t = o['@type'];
        var types = (Object.prototype.toString.call(t) === '[object Array]') ? t : [t];
        if (types.indexOf('BreadcrumbList') >= 0 && o.itemListElement) { list = o.itemListElement; return; }
        for (var key in o) { if (o.hasOwnProperty(key)) walk(o[key]); }
      })(data);
      if (list) { found = list; break; }
    }
    if (!found) return null;
    var arr = [];
    try {
      arr = found.slice(0).sort(function (a, b) { return (a.position || 0) - (b.position || 0); });
    } catch (e) { arr = found; }
    var names = [];
    for (var j = 0; j < arr.length; j++) {
      var n = stripBrand(arr[j] && arr[j].name);
      if (n) names.push(n);
    }
    return names.length ? names : null;
  }

  /* 後備一：頁面可見麵包屑導覽 */
  function fromVisibleCrumb() {
    var sel = '.hsst-crumb, .breadcrumb, .crumbs, nav[aria-label="breadcrumb"], nav[aria-label="Breadcrumb"]';
    var root = document.querySelector(sel);
    if (!root) return null;
    var names = [];
    var nodes = root.querySelectorAll('a, span, li');
    for (var i = 0; i < nodes.length; i++) {
      var t = stripBrand((nodes[i].textContent || '').replace(/\s+/g, ' ').trim());
      if (!t || t === '/' || t === '>' || t === '»' || t === '›') continue;
      if (names.indexOf(t) < 0) names.push(t);
    }
    return names.length ? names : null;
  }

  /* 後備二：og:title → <h1> → <title> */
  function fromTitle() {
    var s = '';
    var og = document.querySelector('meta[property="og:title"]');
    if (og) s = og.getAttribute('content') || '';
    if (!s) { var h1 = document.querySelector('h1'); if (h1) s = h1.textContent || ''; }
    if (!s) s = document.title || '';
    s = stripBrand(s.split(/\s*[|｜]\s*/)[0].trim());
    return s ? (LANG === 'en' ? ['Home', s] : ['首頁', s]) : null;
  }

  function buildTrail(names) {
    if (!names || !names.length) return LANG === 'en' ? 'Home' : '首頁';
    if (names.length === 1) return names[0];
    /* 格式：首頁 / 產品中心 - 精品麻石（倒數兩層以「 - 」連接，其餘用「 / 」） */
    var head = names.slice(0, names.length - 1).join(' / ');
    return head + ' - ' + names[names.length - 1];
  }

  var CACHE = null;      /* {trail, leaf} */
  function resolve() {
    if (CACHE) return CACHE;
    var names = fromJsonLd() || fromVisibleCrumb();
    if (!names) {
      /* 首頁（含 /en/）沒有麵包屑 → 直接用首頁節點 */
      var path = '';
      try {
        path = (String(window.location.pathname) || '/').replace(/\/index\.html?$/i, '/');
      } catch (e) { path = '/'; }
      if (path === '/' || path === '' || path === '/en' || path === '/en/') {
        names = LANG === 'en' ? ['Home'] : ['首頁'];
      } else {
        names = fromTitle();
      }
    }
    var leaf = names[names.length - 1] || (LANG === 'en' ? 'Home' : '首頁');
    CACHE = { trail: buildTrail(names), leaf: leaf };
    return CACHE;
  }

  function trail() { return resolve().trail; }

  function currentUrl() {
    try {
      var u = String(window.location.href);
      var i = u.indexOf('#');
      return i >= 0 ? u.slice(0, i) : u;
    } catch (e) { return ''; }
  }

  /* ---------------- 來源頁覆寫（「索取樣板」等中轉頁場景）----------------
     訪客從某個具體內容頁（工程案例 / 產品 / 攻略…）點擊「索取樣板」連結時，
     連結會帶 ?from=<來源頁絕對路徑>&from_title=<來源頁麵包屑> 跳轉到
     sample-request.html。此時表單「真實發生」在來源頁，郵件必須如實呈現來源頁，
     而非中轉頁本身。若連結未帶參數，則以 document.referrer（同源）作為後備來源。 */
  function getQuery(name) {
    try {
      var m = new RegExp('[?&]' + name + '=([^&#]*)').exec(window.location.search);
      return m ? decodeURIComponent(m[1].replace(/\+/g, ' ')) : '';
    } catch (e) { return ''; }
  }
  function absUrl(u) {
    try { var a = document.createElement('a'); a.href = u; return a.href; } catch (e) { return u; }
  }
  function sameOrigin(u) {
    try { var a = document.createElement('a'); a.href = u; return a.hostname === window.location.hostname; }
    catch (e) { return false; }
  }
  var ORIGIN_TRAIL = null;   /* 來源頁麵包屑（referrer 場景下非同步抓取後快取） */
  function pathTrail(u) {
    try {
      var a = document.createElement('a'); a.href = u;
      var seg = (a.pathname || '').replace(/\/index\.html?$/i, '/').replace(/\.html?$/i, '');
      var parts = seg.replace(/^\/+/, '').replace(/\/+$/, '').split('/').filter(Boolean);
      if (!parts.length) return LANG === 'en' ? 'Home' : '首頁';
      return (LANG === 'en' ? 'Home' : '首頁') + ' / ' + parts[parts.length - 1].replace(/-/g, ' ');
    } catch (e) { return LANG === 'en' ? 'Home' : '首頁'; }
  }
  function lastSegOf(trail) {
    if (!trail) return LANG === 'en' ? 'Home' : '首頁';
    var parts = trail.split('/');
    var last = parts[parts.length - 1] || '';
    var dash = last.split('-');
    return (dash[dash.length - 1] || last || (LANG === 'en' ? 'Home' : '首頁')).trim();
  }
  function fetchOriginTrail(u) {
    if (!u || ORIGIN_TRAIL) return;
    try {
      fetch(u, { credentials: 'omit' }).then(function (r) { return r.text(); }).then(function (html) {
        var blocks = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g) || [];
        for (var i = 0; i < blocks.length; i++) {
          var raw = blocks[i].replace(/<script type="application\/ld\+json">/, '').replace(/<\/script>/, '');
          var data; try { data = JSON.parse(raw); } catch (e) { continue; }
          var found = null;
          (function walk(o) {
            if (found) return;
            if (Object.prototype.toString.call(o) === '[object Array]') { for (var k = 0; k < o.length; k++) walk(o[k]); return; }
            if (!o || typeof o !== 'object') return;
            var t = o['@type']; var types = (Object.prototype.toString.call(t) === '[object Array]') ? t : [t];
            if (types.indexOf('BreadcrumbList') >= 0 && o.itemListElement) { found = o.itemListElement; return; }
            for (var key in o) { if (o.hasOwnProperty(key)) walk(o[key]); }
          })(data);
          if (found) {
            var arr = found.slice(0).sort(function (a, b) { return (a.position || 0) - (b.position || 0); });
            var names = [];
            for (var j = 0; j < arr.length; j++) { var n = stripBrand(arr[j] && arr[j].name); if (n) names.push(n); }
            if (names.length) ORIGIN_TRAIL = buildTrail(names);
            break;
          }
        }
      }).catch(function () {});
    } catch (e) {}
  }
  function originOverride() {
    var f = getQuery('from');
    if (f) {
      var fu = absUrl(f);
      if (sameOrigin(fu)) return { url: fu, title: getQuery('from_title'), via: 'param' };
    }
    var ref = '';
    try { ref = document.referrer || ''; } catch (e) {}
    if (ref && sameOrigin(ref)) {
      var cur = '';
      try { cur = String(window.location.href).split('#')[0]; } catch (e) {}
      if (ref.replace(/\/+$/, '') !== cur.replace(/\/+$/, '')) return { url: ref, title: '', via: 'referer' };
    }
    return null;
  }

  /* ---------------- 表單實例標識（form_id）----------------
     每個表單一個穩定、唯一、ASCII 的實例 ID（如
     inquiry-granite-black-galaxy / products-brochure），用於在通知郵件
     與 splitforms 後台精準點名「具體是哪個表單」。靜態 HTML 已內建，
     此處確保其存在（動態插入的表單則兜底推算）。 */
  function computeFormId(form, urlOverride) {
    /* 1) 優先取靜態注入的 form_id */
    try {
      var ef = form.querySelector('input[type="hidden"][name="form_id"]');
      if (ef && ef.value) return ef.value;
    } catch (e) {}
    /* 2) 否則按「路徑 slug + _subject 用途」兜底推算 */
    var p = '/';
    try {
      if (urlOverride) { var a = document.createElement('a'); a.href = urlOverride; p = a.pathname || '/'; }
      else p = String(window.location.pathname || '/');
    } catch (e) {}
    p = p.replace(/\/index\.html?$/i, '/').replace(/\.html?$/i, '');
    var seg = p.replace(/^\/+/, '').replace(/\/+$/, '').split('/').filter(Boolean);
    var slug = seg.join('-');
    if (slug === 'en') slug = 'en-home';
    else if (slug === '' || slug === 'index') slug = 'home';
    var subj = '';
    try {
      var s = form.querySelector('input[type="hidden"][name="_subject"], input[type="hidden"][name="subject"]');
      if (s) subj = (s.value || '').toLowerCase();
    } catch (e) {}
    var kind = 'inquiry';
    if (/brochure|畫冊|catalog/.test(subj)) kind = 'brochure';
    else if (/sample|樣板/.test(subj)) kind = 'sample';
    else if (/subscribe|訂閱|newsletter|subscription/.test(subj)) kind = 'subscribe';
    else if (/apply|投遞|cv|簡歷|resume/.test(subj)) kind = 'apply';
    else if (/contact|聯繫|聯絡/.test(subj)) kind = 'contact';
    else {
      var rl = p.toLowerCase();
      if (/apply|careers/.test(rl)) kind = 'apply';
      else if (/sample/.test(rl)) kind = 'sample';
      else if (/contact/.test(rl)) kind = 'contact';
      else if (/news/.test(rl)) kind = 'subscribe';
      else if (/brochure/.test(rl)) kind = 'brochure';
    }
    if (slug === kind || slug.indexOf('-' + kind) >= 0 || slug.indexOf(kind + '-') === 0) return slug;
    return slug + '-' + kind;
  }

  /* ---------------- 寫入表單隱藏欄位 ---------------- */
  function setField(form, name, value) {
    var el = null;
    try { el = form.querySelector('input[type="hidden"][name="' + name + '"]'); } catch (e) {}
    if (!el) {
      el = document.createElement('input');
      el.type = 'hidden';
      el.name = name;
      el.setAttribute('data-hsst-auto', '1');
      el.value = value;
      form.appendChild(el);
      return;
    }
    el.value = value;
  }

  function subjectSuffix() {
    var r = resolve();
    /* 主旨尾綴只取最後一段（頁面 / 產品名），過長則截斷 */
    var leaf = r.leaf;
    if (leaf.length > 26) leaf = leaf.slice(0, 26) + '…';
    return { leaf: leaf, trail: r.trail };
  }

  function apply(form) {
    if (!form || !form.action) return;
    if (String(form.action).indexOf('splitforms.com') < 0) return;
    try {
      var ov = originOverride();
      var to, url, fid;
      if (ov) {
        /* 中轉頁（如 sample-request.html）場景：表單真實發生在「來源頁」 */
        url = ov.url;
        var trailStr = (ov.title && ov.title.trim()) ? ov.title.trim() : (ORIGIN_TRAIL || pathTrail(ov.url));
        var leaf = lastSegOf(trailStr);
        to = { trail: trailStr, leaf: leaf };
        if (!ov.title && !ORIGIN_TRAIL) fetchOriginTrail(ov.url);  /* referrer 場景：非同步補抓麵包屑 */
        /* form_id 帶上來源頁 slug，使後台/郵件可精準點名「來自哪個頁面的樣板索取」 */
        try {
          var oa = document.createElement('a'); oa.href = ov.url;
          var oslug = (oa.pathname || '').replace(/\.html?$/i, '').replace(/^\/+/, '').replace(/\/+$/, '').replace(/\//g, '-') || 'home';
          var okind = 'sample';
          var osub = form.querySelector('input[type="hidden"][name="_subject"], input[type="hidden"][name="subject"]');
          if (osub) { var ov2 = (osub.value || '').toLowerCase(); if (/brochure|畫冊|catalog/.test(ov2)) okind = 'brochure'; else if (/subscribe|訂閱/.test(ov2)) okind = 'subscribe'; }
          fid = 'sample-request-' + oslug;
          if (okind !== 'sample') fid = fid.replace(/^sample-request-/, okind + '-');
        } catch (e) { fid = computeFormId(form, ov.url); }
      } else {
        to = subjectSuffix();
        url = currentUrl();
        fid = computeFormId(form);
      }
      setField(form, 'source_page', to.trail);
      setField(form, 'page_url', url);
      setField(form, 'form_id', fid);
      setField(form, 'source_details',
        T('Source Page: ', '來源頁面：') + to.trail + '\n' +
        T('Page URL: ', '頁面連結：') + url + '\n' +
        T('Form ID: ', '表單標識：') + fid);

      /* 主旨尾綴（保留原 _subject 前置標籤，同一輪重複送出不會疊加） */
      var sub = form.querySelector('input[type="hidden"][name="_subject"], input[type="hidden"][name="subject"]');
      var created = false;
      if (!sub) {
        /* 原本沒有主旨欄位（如聯絡表單）→ 建立一個含來源標記的預設主旨 */
        sub = document.createElement('input');
        sub.type = 'hidden';
        sub.name = '_subject';
        created = true;
        form.appendChild(sub);
      }
      if (created || !sub.getAttribute('data-hsst-subject-origin')) {
        sub.setAttribute('data-hsst-subject-origin', created ? '' : (sub.value || ''));
      }
      var base = sub.getAttribute('data-hsst-subject-origin') || '';
      var leaf = to.leaf;
      if (base && base.indexOf(leaf) >= 0) {
        sub.value = base;                       /* 原主旨已含頁/產品名 → 不再重複附加 */
      } else if (base) {
        sub.value = base + T(' | ', ' ｜ ') + T('Source: ', '來源：') + leaf;
      } else {
        sub.value = T('New website enquiry', '網站表單新提交') + T(' | ', ' ｜ ') + T('Source: ', '來源：') + leaf;
      }
    } catch (e) {}
  }

  function applyAll(scope) {
    var root = scope || document;
    var forms = root.querySelectorAll ? root.querySelectorAll('form') : [];
    for (var i = 0; i < forms.length; i++) apply(forms[i]);
  }

  /* 除錯用：可在 console 執行 __hsstSourceInfo() 查看 */
  window.__hsstSourceInfo = function () {
    return { url: currentUrl(), trail: trail(), subjectLeaf: subjectSuffix().leaf };
  };

  /* ① 送出前的捕獲階段：一定趕在任何人取 FormData 之前補寫（最先註冊） */
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f && f.tagName === 'FORM') { CACHE = null; apply(f); }
  }, true);

  /* ② DOM 就緒後補寫（含延後插入的彈窗表單） */
  function boot() { applyAll(document); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  /* ③ 動態新增表單（彈窗 / 延遲載入）也能自動補上 */
  if (window.MutationObserver) {
    var mo = new MutationObserver(function (muts) {
      for (var i = 0; i < muts.length; i++) {
        var added = muts[i].addedNodes;
        for (var j = 0; j < added.length; j++) {
          var n = added[j];
          if (!n || n.nodeType !== 1) continue;
          if (n.tagName === 'FORM') apply(n);
          else if (n.querySelectorAll) applyAll(n);
        }
      }
    });
    var startMO = function () {
      try { mo.observe(document.body, { childList: true, subtree: true }); } catch (e) {}
    };
    if (document.body) startMO(); else addEventListener('DOMContentLoaded', startMO);
  }

  /* ④ 使用者開始填寫時再刷新一次（應對站內 pushState 換址） */
  document.addEventListener('focusin', function (e) {
    var form = e.target && e.target.form;
    if (form) { CACHE = null; apply(form); }
  }, true);
})();
