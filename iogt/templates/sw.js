importScripts('../../static/js/workbox/workbox-v6.1.5/workbox-sw.js');

// Below we are using a custom dimension to track online vs. offline interactions. So make
// sure to create a custom dimension on GA
workbox.googleAnalytics.initialize({
    parameterOverrides: {
        cd1: 'offline',
    },
});

self.addEventListener('install', event => {
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET')
        return;

    event.respondWith(
        fetch(event.request)
            .then(resp => {
                return caches.open('iogt')
                    .then(cache => {
                        return cache.match(event.request).then(match => {
                            if (match) {
                                cache.delete(event.request);
                                cache.put(event.request, resp.clone());
                            }
                            return resp;
                        })
                    });
            })
            .catch(error => {
                return caches.open('iogt')
                    .then(cache => {
                        return cache.match(event.request.url)
                    });
            })
    );
});
