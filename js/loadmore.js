/* ============================================================
   HENGSHENG MARBLE — Load More v1.0
   自动将 [data-loadmore-batch] 的子项分批展示
   ============================================================ */
(function () {
  'use strict';
  if (window.__HSST_LOADMORE_LOADED__) return;
  window.__HSST_LOADMORE_LOADED__ = true;

  function init() {
    var containers = document.querySelectorAll('[data-loadmore]');
    containers.forEach(function (box) {
      var items = Array.prototype.slice.call(box.children);
      var batch = parseInt(box.getAttribute('data-loadmore-batch') || '6', 10);
      var i18n = {
        zh: '載入更多',
        en: 'Load more'
      };
      var lang = (document.documentElement.lang || '').toLowerCase().startsWith('en') ? 'en' : 'zh';

      if (!items.length) return;
      var shown = 0;
      function show(n) {
        for (var k = 0; k < n && shown < items.length; k++) {
          items[shown].style.display = '';
          shown++;
        }
      }
      function hide() {
        items.forEach(function (it) { it.style.display = 'none'; });
        shown = 0;
      }
      function apply() {
        hide();
        show(batch);
      }
      // 初始：先全部隐藏再展示一批
      apply();

      // 按钮
      var btnId = box.getAttribute('data-loadmore-btn');
      var btn = btnId ? document.getElementById(btnId) : box.parentElement.querySelector('[data-loadmore-trigger]');
      if (!btn) {
        btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'hsst-loadmore-btn';
        btn.setAttribute('data-loadmore-trigger', '');
        btn.textContent = i18n[lang];
        box.insertAdjacentElement('afterend', btn);
      }
      btn.addEventListener('click', function () {
        show(batch);
        if (shown >= items.length) {
          btn.style.display = 'none';
        }
      });
      if (shown >= items.length) btn.style.display = 'none';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();