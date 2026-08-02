// Service Worker - 课时记录 PWA
// 每次部署新版本时，修改下方 VERSION 即可触发更新
const VERSION = 'v4.0.18';
const CACHE_NAME = 'keshi-app-' + VERSION;

// 需要预缓存的静态资源（版本不变则走缓存，版本升级则重新下载）
const PRE_CACHE = [
  './manifest.webmanifest',
  './icons/icon-72.png',
  './icons/icon-96.png',
  './icons/icon-120.png',
  './icons/icon-144.png',
  './icons/icon-152.png',
  './icons/icon-167.png',
  './icons/icon-180.png',
  './icons/icon-192.png',
  './icons/icon-256.png',
  './icons/icon-512.png',
  './assets/wechat-qr.jpg',
  './assets/alipay-qr.jpg'
];

// 安装：预缓存静态资源
self.addEventListener('install', e => {
  self.skipWaiting(); // 跳过等待，直接激活新版本
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(PRE_CACHE))
  );
});

// 激活：清理旧缓存 + 接管所有客户端
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// 拦截请求
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;

  const url = new URL(e.request.url);

  // index.html：网络优先（保证每次都拿到最新版）
  if (url.pathname.endsWith('/') || url.pathname.endsWith('/index.html')) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          // 网络成功，缓存一份供离线使用
          const resClone = res.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, resClone));
          return res;
        })
        .catch(() => caches.match(e.request)) // 离线时走缓存
    );
    return;
  }

  // 其他静态资源：缓存优先
  e.respondWith(
    caches.match(e.request).then(cached =>
      cached || fetch(e.request).then(res => {
        const resClone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, resClone));
        return res;
      })
    )
  );
});

// 接收主线程消息（用于触发更新检查）
self.addEventListener('message', e => {
  if (e.data === 'skip-waiting') {
    self.skipWaiting();
  }
});
