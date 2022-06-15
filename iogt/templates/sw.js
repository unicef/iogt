importScripts('../../static/js/workbox/workbox-v6.1.5/workbox-sw.js');

// Below we are using a custom dimension to track online vs. offline interactions. So make
// sure to create a custom dimension on GA
workbox.googleAnalytics.initialize({
    parameterOverrides: {
        cd1: 'offline',
    },
});

self.addEventListener('install', event => {
    console.log('Service worker installed.');
});

self.addEventListener('activate', event => {
    console.log('Service worker activated.');
});

self.addEventListener('fetch', event => {
    console.log('Responding to', event.request.url);
    event.respondWith(
        fetch(event.request)
            .then(resp => {
                console.log('Fetched successfully.', event.request.url);
                return resp;
            })
            .catch(error => {
                console.log('Unable to fetch.', event.request.url, error);
                return caches.open('iogt')
                    .then(cache => {
                        console.log('Trying cache for ', event.request.url);
                        return cache.match(event.request.url)
                    });
            })
    );
});
