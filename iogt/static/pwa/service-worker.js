/* global workbox */
importScripts('https://storage.googleapis.com/workbox-cdn/releases/6.6.0/workbox-sw.js');

if (self && workbox) {
  // Fast SW updates
  self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') self.skipWaiting();
  });
  workbox.core.clientsClaim();

  const PRECACHE_VERSION = 'v1.0.0';

  // Precache core shell
  workbox.precaching.precacheAndRoute([
    {url: '/', revision: null}, // network-first below keeps it fresh
    {url: '/static/pwa/offline.html', revision: PRECACHE_VERSION},
  ]);

  // HTML pages – NetworkFirst for freshness
  workbox.routing.registerRoute(
    ({request}) => request.destination === 'document',
    new workbox.strategies.NetworkFirst({
      cacheName: 'html-pages',
      networkTimeoutSeconds: 6,
      plugins: [
        new workbox.expiration.ExpirationPlugin({maxEntries: 200, maxAgeSeconds: 7 * 24 * 3600}),
      ],
    })
  );

  // Static assets – StaleWhileRevalidate
  workbox.routing.registerRoute(
    ({request}) => ['style', 'script', 'worker'].includes(request.destination),
    new workbox.strategies.StaleWhileRevalidate({
      cacheName: 'static-assets',
      plugins: [
        new workbox.expiration.ExpirationPlugin({maxEntries: 400, maxAgeSeconds: 30 * 24 * 3600}),
      ],
    })
  );

  // Images – CacheFirst
  workbox.routing.registerRoute(
    ({request}) => request.destination === 'image',
    new workbox.strategies.CacheFirst({
      cacheName: 'images',
      plugins: [
        new workbox.expiration.ExpirationPlugin({maxEntries: 400, maxAgeSeconds: 30 * 24 * 3600}),
      ],
    })
  );

  // Wagtail/REST JSON endpoints – NetworkFirst (tweak prefix if you use something else)
  workbox.routing.registerRoute(
    ({url}) => url.pathname.startsWith('/api/'),
    new workbox.strategies.NetworkFirst({cacheName: 'api', networkTimeoutSeconds: 5})
  );

  // Background Sync for form POSTs (adjust paths to your forms)
  const bgSyncPlugin = new workbox.backgroundSync.BackgroundSyncPlugin('formQueue', {
    maxRetentionTime: 24 * 60, // minutes
  });
  workbox.routing.registerRoute(
    ({request, url}) => request.method === 'POST' && (
      url.pathname.startsWith('/forms/') ||
      url.pathname.includes('/submit') ||
      url.pathname.includes('/contact')
    ),
    new workbox.strategies.NetworkOnly({plugins: [bgSyncPlugin]}),
    'POST'
  );

  // Offline fallback for navigations
  workbox.routing.setCatchHandler(async ({event}) => {
    if (event.request.destination === 'document') {
      return caches.match('/static/pwa/offline.html', {ignoreSearch: true});
    }
    return Response.error();
  });

  // Push Notifications (payload: {title, body, icon, badge, data:{url}})
  self.addEventListener('push', (event) => {
    if (!event.data) return;
    const data = event.data.json();
    event.waitUntil(self.registration.showNotification(
      data.title || 'Notification',
      {
        body: data.body || '',
        icon: data.icon || '/static/pwa/icons/icon-192.png',
        badge: data.badge || '/static/pwa/icons/icon-192.png',
        data: data.data || {},
        actions: data.actions || [],
      }
    ));
  });

  self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const url = (event.notification?.data && event.notification.data.url) || '/';
    event.waitUntil(clients.openWindow(url));
  });

} else {
  // No workbox; keep SW valid to avoid 404 loops
  self.addEventListener('fetch', () => {});
}
