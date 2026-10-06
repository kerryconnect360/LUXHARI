const CACHE = 'luxhari-public-v3';
const STATIC = [
  '/', '/manifest.json', '/static/css/luxhari.css', '/static/js/luxhari.js', '/static/icons/luxhari-192.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(c => c.addAll(STATIC)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});

function isPrivate(pathname) {
  return pathname.startsWith('/admin') || pathname.startsWith('/cart') || pathname.startsWith('/checkout') || pathname.startsWith('/track') || pathname.startsWith('/interests') || pathname.startsWith('/orders');
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || isPrivate(url.pathname) || url.pathname === '/service-worker.js') return;

  event.respondWith(
    caches.match(request).then(cached => cached || fetch(request).then(response => {
      if (response.ok && (request.destination === 'image' || request.destination === 'style' || request.destination === 'script' || url.pathname === '/' || url.pathname === '/manifest.json')) {
        const copy = response.clone();
        caches.open(CACHE).then(c => c.put(request, copy));
      }
      return response;
    }).catch(() => caches.match('/')))
  );
});
