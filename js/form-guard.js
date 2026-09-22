/* =================================================================
   [CRITICAL CODE - DO NOT DELETE OR MODIFY / 核心代碼 嚴禁刪除]
   HSST 全站表單「統一提交守衛」（Form Guard）— 單一來源（js/form-guard.js）
   -----------------------------------------------------------------
   PROJECT : HSST 全站表單（endpoint: splitforms.com）
   PURPOSE : ① 確保每次有效提交「只寄一封」通知郵件（去重上鎖 + 單發）
             ② 所有表單提交成功後，統一展示與「索取样板」一致的提示頁
   ROOT CAUSE（已修復）:
     過去「頁面自訂 submit 處理器」與「全域 splitforms 處理器」各自執行
     一次 fetch，且全域處理器註冊於「捕獲階段」早于頁面校驗執行，
     造成 ① 一次提交寄出兩封郵件 ② 校驗失敗仍會寄出郵件。
   HOW IT WORKS:
     ① 捕獲階段 — 只做「去重上鎖」，永不發信
     ② 頁面處理器 — 只負責「校驗」（無效時 preventDefault；有效時交給守衛）
     ③ 冒泡階段 — 僅在「本輪無人發送過 AND 校驗通過」時才由全域補發一次
   WARNING: 刪除或改動本段將導致表單重複寄信或失效，請勿修改。
   ================================================================= */
(function () {
  "use strict";
  if (window.__HSST_FORM_GUARD__) return;
  window.__HSST_FORM_GUARD__ = true;

  var ENDPOINT = 'splitforms.com';
  var LOCK_MS  = 5000;
  var LANG = (document.documentElement.lang || '').toLowerCase().indexOf('en') === 0 ? 'en' : 'zh';
  var T = function (en, zh) { return LANG === 'en' ? en : zh; };

  /* ---------- 注入成功提示頁 + toast 的樣式（自包含，全站通用） ---------- */
  function injectStyles() {
    if (document.getElementById('hsst-guard-style')) return;
    var css = [
      '.hsst-success-panel{display:none;text-align:center;padding:48px 24px;',
      'background:#FFFFFF;border:1px solid #E6DCC8;border-top:4px solid #C9A84C;border-radius:16px;',
      'max-width:560px;margin:24px auto;box-shadow:0 20px 60px rgba(0,0,0,0.10);}',
      '.hsst-success-panel.show{display:block;animation:hsstPop .35s ease;}',
      '@keyframes hsstPop{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}',
      '.hsst-success-panel .hsst-success-icon{font-size:48px;margin-bottom:16px;color:#C9A84C;}',
      '.hsst-success-panel h3{color:#1A1A1A;font-size:20px;margin:0 0 8px;font-family:"Noto Serif TC",serif;}',
      '.hsst-success-panel p{color:#444444;font-size:15px;line-height:1.8;margin:0;}',
      '.hsst-success-panel p b{color:#1A1A1A;font-weight:700;}',
      '.hsst-form-toast{position:fixed;left:50%;bottom:32px;transform:translateX(-50%) translateY(20px);',
      'background:rgba(20,20,38,0.96);color:#fff;padding:14px 22px;border-radius:10px;font-size:14px;',
      'border:1px solid rgba(201,168,76,0.35);z-index:99999;opacity:0;pointer-events:none;',
      'transition:opacity .25s ease,transform .25s ease;max-width:90vw;}',
      '.hsst-form-toast.show{opacity:1;transform:translateX(-50%) translateY(0);}',
      '.hsst-form-toast.error{border-color:#e74c3c;}'
    ].join('');
    var st = document.createElement('style');
    st.id = 'hsst-guard-style';
    st.textContent = css;
    document.head.appendChild(st);
  }

  function isOurForm(f) {
    return !!(f && f.action && String(f.action).indexOf(ENDPOINT) >= 0);
  }

  function toast(msg, type) {
    var t = document.getElementById('hsst-form-toast');
    if (!t) {
      t = document.createElement('div');
      t.id = 'hsst-form-toast';
      t.className = 'hsst-form-toast';
      document.body.appendChild(t);
    }
    t.className = 'hsst-form-toast show ' + (type || 'success');
    t.textContent = msg;
    clearTimeout(t.__timer);
    t.__timer = setTimeout(function () { t.className = 'hsst-form-toast'; }, 4500);
  }
  window.__hsstFormToast = toast;

  function unlock(f) {
    if (!f) return;
    f.__hsstBusy = false;
    clearTimeout(f.__hsstLockT);
  }
  window.__hsstUnlock = unlock;
  window.__hsstMarkSent = function (f) { if (f) f.__hsstSent = true; };

  /* 校驗安全網：required 必填 / email 格式 / 必勾選 */
  function validate(f) {
    var ok = true;
    f.querySelectorAll('[required]').forEach(function (el) {
      var ty = (el.type || '').toLowerCase();
      if (ty === 'checkbox' || ty === 'radio') { if (!el.checked) ok = false; }
      else if (!String(el.value || '').trim()) ok = false;
    });
    f.querySelectorAll('input[type="email"][required]').forEach(function (el) {
      var v = String(el.value || '').trim();
      if (v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) ok = false;
    });
    return ok;
  }

  /* 統計「本輪事件內」已發出的請求數，供去重判斷 */
  window.__hsstSendCount = 0;
  window.__hsstActiveForm = null;
  var _fetch = window.fetch;
  if (typeof _fetch === 'function') {
    window.fetch = function () {
      var isOurs = false;
      try {
        var u = arguments[0];
        var s = (typeof u === 'string') ? u : ((u && u.url) || '');
        isOurs = String(s).indexOf(ENDPOINT) >= 0;
      } catch (e) {}
      var p = _fetch.apply(window, arguments);
      if (isOurs) {
        window.__hsstSendCount++;
        var done = function () { unlock(window.__hsstActiveForm); };
        try { p.then(done, done); } catch (e) {}
      }
      return p;
    };
  }

  /* ---------- 統一成功提示頁（對齊「索取样板」#sampleSuccess） ---------- */
  function showSuccess(f) {
    if (!f) return;
    // 若頁面已有專屬成功面板（如 sample-request 的 #sampleSuccess），優先復用
    var existing = null;
    var parent = f.parentElement;
    while (parent && !existing) {
      existing = parent.querySelector('#sampleSuccess, .sample-form-success, .hsst-form-success');
      if (existing) break;
      parent = parent.parentElement;
    }
    if (existing) {
      try { f.style.display = 'none'; } catch (e) {}
      existing.style.display = 'block';
      existing.classList.add('show');
      try { existing.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) {}
      return;
    }
    // 否則注入與「索取样板」一致風格的成功提示頁
    var panel = document.createElement('div');
    panel.className = 'hsst-success-panel';
    panel.setAttribute('role', 'status');
    panel.setAttribute('aria-live', 'polite');
    if (LANG === 'en') {
      panel.innerHTML =
        '<div class="hsst-success-icon">📦</div>' +
        '<h3>✓ Submission received!</h3>' +
        '<p>Thank you. Our specialist will contact you within <b>24 hours</b> to confirm ' +
        'your request and arrange the next steps. For urgent matters, call <b>+852 5538 0525</b> ' +
        'or email <b>stone@hsst.hk</b>.</p>';
    } else {
      panel.innerHTML =
        '<div class="hsst-success-icon">📦</div>' +
        '<h3>✓ 提交成功！</h3>' +
        '<p>感謝您的提交。我們的專員將於 <b>24 小時內</b> 與您聯繫，確認需求並安排後續事宜。' +
        '如需緊急處理，請致電 <b>+852 5538 0525</b> 或發送郵件至 <b>stone@hsst.hk</b>。</p>';
    }
    // 同步顯示（不依賴 requestAnimationFrame，避免部分環境動畫回調不觸發導致「提交後無提示」）
    panel.classList.add('show');
    try {
      if (f.parentElement) f.parentElement.insertBefore(panel, f.nextSibling);
      else document.body.appendChild(panel);
    } catch (e) {
      try { document.body.appendChild(panel); } catch (e2) {}
    }
    try { f.style.display = 'none'; } catch (e) {}
    requestAnimationFrame(function () { panel.classList.add('show'); });
    try { panel.scrollIntoView({ behavior: 'smooth', block: 'center' }); } catch (e) {}
  }
  window.__hsstShowSuccess = showSuccess;

  /* ① 捕獲階段：去重上鎖，絕不發信 */
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!isOurForm(f)) return;
    window.__hsstSendCount = 0;
    f.__hsstSent = false;
    if (f.__hsstBusy) {
      e.preventDefault();
      e.stopImmediatePropagation();   /* 重複觸發：直接掐斷，不再向下傳遞 */
      return;
    }
    f.__hsstBusy = true;
    window.__hsstActiveForm = f;
    var btn = f.querySelector('button[type="submit"], input[type="submit"]');
    if (btn) {
      f.__hsstBtn = btn;
      f.__hsstBtnText = btn.textContent;
      f.__hsstBtnDisabled = btn.disabled;
    }
    clearTimeout(f.__hsstLockT);
    f.__hsstLockT = setTimeout(function () { unlock(f); }, LOCK_MS);
    e.__hsstGuardPass = true;
  }, true);

  /* ② 冒泡階段：頁面處理器跑完後，才決定是否發信 */
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!isOurForm(f) || !e.__hsstGuardPass) return;
    e.preventDefault();                  /* 一律阻止瀏覽器整頁跳轉 */
    if (window.__hsstSendCount > 0 || f.__hsstSent) return;  /* 頁面已自行發送 → 不重發 */
    if (!validate(f)) { unlock(f); return; }                 /* 校驗未過 → 不寄信（守衛為唯一判斷依據，不受頁面 preventDefault 影響） */
    sendOnce(f);
  }, false);

  function sendOnce(f) {
    var btn = f.__hsstBtn;
    if (btn) { btn.disabled = true; btn.textContent = T('Sending…', '送出中…'); }
    fetch(f.action, {
      method: 'POST',
      body: new FormData(f),
      headers: { 'Accept': 'application/json' }
    }).then(function (r) {
      if (r.ok || r.status === 200 || r.status === 201 || r.status === 0) {
        showSuccess(f);                 /* 統一成功提示頁（對齊「索取样板」） */
        try { f.reset(); } catch (e) {}
      } else {
        toast(T('Submission failed, please try again later.', '提交失敗，請稍後再試'), 'error');
      }
      if (btn) { btn.disabled = false; btn.textContent = f.__hsstBtnText; }
      unlock(f);
    }).catch(function () {
      toast(T('Submission failed, please try again later.', '提交失敗，請稍後再試'), 'error');
      if (btn) { btn.disabled = false; btn.textContent = f.__hsstBtnText; }
      unlock(f);
    });
  }

  /* 頁面就緒後注入樣式 */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectStyles);
  } else {
    injectStyles();
  }
})();
