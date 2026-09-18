/*!
 * hsst.hk 全站「返回上頁」浮動按鈕
 * -----------------------------------
 * 規則（純前端依 pathname 推導，頁面零配置）：
 *   · 語言根：/en/ 前綴 → EN 文案；其餘 → 繁體文案
 *   · 目錄頁（products/white-marble.html 等）→ 上級 = 該目錄同名著陸頁
 *   · 嵌套詳情頁（products/<系列>/<品種>.html 等 dir/a/b.html）→ 上級 = 子目錄著陸頁
 *   · 語言根一級頁（about.html 等）→ 上級 = 語言根首頁
 *   · 語言根首頁（index.html / en/index.html）→ 不顯示
 *   · 未知目錄 → 不顯示（防 404）
 * 樣式自包含（JS 注入 <style>），不依賴任何 CSS 檔，改版只動本檔。
 * ⚠️ 實測本檔 CDN 頭為 max-age=0,must-revalidate（非 immutable）：改本檔無需遞增 ?v= 令牌。
 */
(function () {
  "use strict";

  var seg = location.pathname.split("/").filter(Boolean);
  var isEn = seg[0] === "en";
  var rest = isEn ? seg.slice(1) : seg;
  if (rest.length === 0) return;                    // 語言根首頁
  if (rest.length === 1 && rest[0] === "index.html") return;

  /* 目錄 → 同名著陸頁 + 雙語文案（新目錄頁加入這裡即可） */
  var DIRS = {
    products:    { zh: "返回產品中心", en: "Back to Products" },
    projects:    { zh: "返回工程案例", en: "Back to Projects" },
    news:        { zh: "返回新聞動態", en: "Back to News" },
    careers:     { zh: "返回人才招聘", en: "Back to Careers" },
    technology:  { zh: "返回技術中心", en: "Back to Technology" },
    solutions:   { zh: "返回解決方案", en: "Back to Solutions" }
  };

  /* 嵌套詳情頁（dir/<子目錄>/x.html）的上一頁文案；未列出的目錄用通用文案 */
  var SUB_LABELS = {
    products: { zh: "返回系列", en: "Back to Series" }
  };

  /* new Array(n).join(x) 產生 n-1 個分隔符；rest.length 段（含檔名）需要 rest.length-1 層 ../ */
  var prefix = rest.length > 1 ? new Array(rest.length).join("../") : "";
  var parent, label;
  if (rest.length === 1) {                          // 語言根一級頁 → 首頁
    parent = prefix + "index.html";
    label = isEn ? "Back to Home" : "返回首頁";
  } else {
    var dir = rest[0], d = DIRS[dir];
    if (!d) return;                                 // 未知目錄不顯示
    if (rest.length >= 3) {                         // 嵌套詳情頁 → 子目錄著陸頁
      var sub = rest[rest.length - 2];
      parent = prefix + dir + "/" + sub + ".html";
      var sd = SUB_LABELS[dir];
      label = isEn ? (sd ? sd.en : "Back") : (sd ? sd.zh : "返回上頁");
    } else {
      parent = prefix + dir + ".html";
      label = isEn ? d.en : d.zh;
    }
  }

  var ARROW =
    '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true" focusable="false">' +
    '<path d="M15 5l-7 7 7 7" fill="none" stroke="currentColor" stroke-width="2.4" ' +
    'stroke-linecap="round" stroke-linejoin="round"/></svg>';

  var css = [
    /* 桌面：右下角列自下而上 = WhatsApp 球(26) → 回到頂部(90,高44) → 本按鈕(148) */
    ".hsst-back{position:fixed;bottom:148px;right:22px;z-index:1500;display:inline-flex;align-items:center;gap:7px;",
    "padding:10px 13px 10px 17px;border-radius:999px;background:rgba(26,26,46,.92);",
    "border:1px solid rgba(201,168,76,.45);color:#C9A84C;font:600 13px/1 -apple-system,BlinkMacSystemFont,'PingFang TC','Microsoft JhengHei',sans-serif;",
    "letter-spacing:.04em;text-decoration:none;box-shadow:0 6px 20px rgba(0,0,0,.28);",
    "transition:transform .25s ease,border-color .25s ease,background .25s ease;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);}",
    ".hsst-back svg{flex:none;transition:transform .25s ease;}",
    ".hsst-back:hover,.hsst-back:focus-visible{transform:translateY(-2px);border-color:#C9A84C;background:rgba(26,26,46,.98);color:#E3C88B;}",
    ".hsst-back:hover svg{transform:translateX(-2px);}",
    ".hsst-back:focus-visible{outline:2px solid #C9A84C;outline-offset:2px;}",
    "body.drawer-open .hsst-back{opacity:0;visibility:hidden;pointer-events:none;}",
    /* ≤768px：右下角「回到頂部」被 premium 釘在 bottom:20px+safe-area（高38），
       本按鈕墊在其上方（70 → 留 12px 縫）；WhatsApp 球在左下，互不干擾。
       斷點必須同步 768px */
    "@media (max-width:768px){.hsst-back{bottom:calc(70px + env(safe-area-inset-bottom,0px));",
    "right:calc(14px + env(safe-area-inset-right,0px));padding:9px 11px 9px 14px;font-size:12px;gap:6px;}}",
    "@media print{.hsst-back{display:none!important}}"
  ].join("\n");

  function boot() {
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);

    var a = document.createElement("a");
    a.className = "hsst-back";
    a.href = parent;
    a.setAttribute("aria-label", label);
    a.innerHTML = ARROW + "<span>" + label + "</span>";
    document.body.appendChild(a);

    /* cookie 横幅是底部通栏（z-index 2000），会盖住并拦截本按钮（z-index 1500）
       —— 横幅可见期间把按钮顶到横幅上方，横幅消失后还原（2026-09-17 真机实测踩坑） */
    var banner = document.getElementById("cookieBanner");
    if (banner) {
      var apply = function () {
        var shown = banner.offsetHeight > 0;
        a.style.bottom = shown ? (banner.offsetHeight + 14) + "px" : "";
      };
      try {
        new MutationObserver(apply).observe(banner, { attributes: true, attributeFilter: ["style", "class"] });
      } catch (e) {}
      window.addEventListener("resize", apply);
      apply();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
