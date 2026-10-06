const CACHE='luxhari-v4';
const SHELL=['/','/static/css/luxhari.css','/static/js/luxhari.js','/manifest.json'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

function isPrivateOrLive(url, request) {
  const path = url.pathname;
  if (request.method !== 'GET') return true;
  if (path.startsWith('/admin')) return true;
  if (path === '/cart' || path.startsWith('/checkout') || path.startsWith('/track') || path.startsWith('/interests') || path.startsWith('/orders')) return true;
  if (path.startsWith('/api') || path.startsWith('/pulse_receiver')) return true;
  return false;
}

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || isPrivateOrLive(url, request)) return;

  // Public image assets are cache-first for a fast visual catalogue.
  if (url.hostname === 'images.pexels.com' || url.pathname.startsWith('/media/')) return;

  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(response => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then(cache => cache.put(request, copy));
        }
        return response;
      }).catch(() => caches.match('/'));
    })
  );
});
