importScripts('../static/third_party/workbox/workbox-v6.1.5/workbox-sw.js');


// Below we are using a custom dimension to track online vs. offline interactions. So make
// sure to create a custom dimension on GA

workbox.googleAnalytics.initialize({
  parameterOverrides: {
    cd1: 'offline',
  },
});

const precacheController = new workbox.precaching.PrecacheController();

self.addEventListener('install', event => {
    const resp = fetch(`${location.protocol}//${location.host}/sitemap/`)
        .then(response => response.json())
        .then(urls => {
            precacheController.addToCacheList(urls.map(url => ({
                url,
                revision: null,
            })));
            workbox.precaching.precacheAndRoute(urls.map(url => ({
                url,
                revision: null,
            })));
        })
        .then(() => {
            // Passing in event is required in Workbox v6+
            precacheController.install(event);
        });
    event.waitUntil(resp);
});
