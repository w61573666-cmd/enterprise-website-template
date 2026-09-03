/* ============================================================
   Service Worker（network-first + 缓存兜底）
   目的：满足 Chrome/Edge 的 PWA 安装条件（beforeinstallprompt），
   同时避免"旧页面缓存"——网络优先，正常情况永远加载最新，
   仅离线时用缓存兜底。配合 ?v= 版本号刷新机制。
   ============================================================ */
var CACHE_NAME = 'hsst-runtime-v1';

self.addEventListener('install', function (e) {
  self.skipWaiting();
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE_NAME; })
        .map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  // 仅处理同源 GET 请求，其余（POST/跨域）直接走网络
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== location.origin) return;

  e.respondWith(
    fetch(req).then(function (response) {
      // 网络优先：成功则缓存一份最新，并返回网络响应
      if (response && response.status === 200 && response.type === 'basic') {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function (cache) {
          cache.put(req, copy);
        });
      }
      return response;
    }).catch(function () {
      // 网络失败（离线）：缓存兜底
      return caches.match(req).then(function (cached) {
        return cached || fetch(req);
      });
    })
  );
});
