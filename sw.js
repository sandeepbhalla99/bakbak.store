const CACHE_NAME = 'bakbak-store-cache-v56';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './css/styles.css',
  './js/app.js',
  './js/books.js',
  './js/auth.js',
  './js/reader.js',
  './js/community.js',
  './books/catalog.json',
  'https://cdn.jsdelivr.net/npm/marked/marked.min.js',
  'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap'
];

// --- Install Service Worker ---
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return Promise.all(
        ASSETS_TO_CACHE.map(url => {
          return cache.add(url).catch(err => {
            console.warn(`Failed to pre-cache asset during install: ${url}`, err);
          });
        })
      );
    }).then(() => self.skipWaiting())
  );
});

// --- Activate Service Worker ---
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Clearing old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// --- Fetch Event (Network First, Cache Fallback) ---
self.addEventListener('fetch', event => {
  // Only handle GET requests and local/CDN requests
  if (event.request.method !== 'GET') return;

  const url = event.request.url;
  if (!url.startsWith(self.location.origin) && 
      !url.startsWith('https://cdn.jsdelivr.net') && 
      !url.startsWith('https://fonts.googleapis.com') &&
      !url.startsWith('https://fonts.gstatic.com')) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(networkResponse => {
        // Cache the newly fetched file dynamically
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Fallback to cache if offline
        return caches.match(event.request);
      })
  );
});
