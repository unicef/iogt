importScripts('../../static/js/workbox/workbox-v6.1.5/workbox-sw.js');

// Below we are using a custom dimension to track online vs. offline interactions. So make
// sure to create a custom dimension on GA
workbox.googleAnalytics.initialize({
    parameterOverrides: {
        cd1: 'offline',
    },
});

const precacheController = new workbox.precaching.PrecacheController();

self.addEventListener('install', (event) => {
    const resp = fetch('/sitemap/')
        .then(response => response.json())
        .then(urls => {
            precacheController.addToCacheList(urls.map(url => ({
                url,
                revision: null,
            })));
        }).then(() => {
            // Passing in event is required in Workbox v6+
            event.waitUntil(precacheController.install(event));
        })
    event.waitUntil(resp);
});

self.addEventListener('activate', (event) => {
    // Passing in event is required in Workbox v6+
    event.waitUntil(precacheController.activate(event));
});

self.addEventListener('fetch', (event) => {
    const cacheKey = precacheController.getCacheKeyForURL(event.request.url);
    event.respondWith(caches.match(cacheKey));
});
