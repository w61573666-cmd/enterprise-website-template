/* ============================================================
   HENGSHENG MARBLE — Stone Filter v1.0
   监听 [data-filter] 按钮组 → 切换 [data-filter-target] 可见
   ============================================================ */
(function () {
  'use strict';
  if (window.__HSST_FILTER_LOADED__) return;
  window.__HSST_FILTER_LOADED__ = true;

  function init() {
    // 每组筛选：[data-filter-group]
    var groups = document.querySelectorAll('[data-filter-group]');
    if (!groups.length) return;

    groups.forEach(function (group) {
      var buttons = group.querySelectorAll('[data-filter]');
      var targetSelector = group.getAttribute('data-filter-target');
      var items = document.querySelectorAll(targetSelector || '[data-filter-item]');
      var multi = group.getAttribute('data-filter-multi') === 'true';

      buttons.forEach(function (btn) {
        // ARIA
        if (!btn.hasAttribute('aria-pressed')) btn.setAttribute('aria-pressed', 'false');
        btn.addEventListener('click', function () {
          var key = btn.getAttribute('data-filter');
          if (multi) {
            var active = btn.classList.toggle('is-active');
            btn.setAttribute('aria-pressed', active ? 'true' : 'false');
          } else {
            buttons.forEach(function (b) { b.classList.remove('is-active'); b.setAttribute('aria-pressed', 'false'); });
            btn.classList.add('is-active');
            btn.setAttribute('aria-pressed', 'true');
          }
          applyFilter();
        });
      });

      function activeKeys() {
        var keys = [];
        buttons.forEach(function (b) { if (b.classList.contains('is-active')) keys.push(b.getAttribute('data-filter')); });
        return keys;
      }

      function applyFilter() {
        var keys = activeKeys();
        // 空选中 = 显示全部
        var any = keys.length > 0;
        var visible = 0;
        items.forEach(function (it) {
          var cat = (it.getAttribute('data-filter-cat') || '').split(/[\s,]+/);
          var show = !any || cat.some(function (c) { return keys.indexOf(c) >= 0; });
          it.style.display = show ? '' : 'none';
          if (show) visible++;
        });
        // 显示空状态
        var emptyEl = document.querySelector(group.getAttribute('data-filter-empty') || '.filter-empty');
        if (emptyEl) emptyEl.style.display = (visible === 0) ? '' : 'none';
      }
      applyFilter();
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();