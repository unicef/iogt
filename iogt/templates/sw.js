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


const languageCodeRegEx = RegExp('^\\/(\\w+([@-]\\w+)?)(\\/|$)');

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET')
        return;

    const languageCode = languageCodeRegEx.exec(new URL(event.request.url).pathname)?.[1] || 'en';
    console.log(languageCode);

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
                        console.log(languageCode);
                        return cache.match(event.request)
                            .then(match => {
                                if (match)
                                    return match;
                                else if (event.request.headers.get('Accept').indexOf('text/html') !== -1)
                                    return cache.match(`/${languageCode}/offline-content-not-found/`);
                            });
                    });
            })
    );
});
