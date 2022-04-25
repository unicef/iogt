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
            precacheController.install(event)
        });
    event.waitUntil(resp);
});

// Register event listener for the 'push' event.
self.addEventListener('push', function (event) {
    // Retrieve the textual payload from event.data (a PushMessageData object).
    // Other formats are supported (ArrayBuffer, Blob, JSON), check out the documentation
    // on https://developer.mozilla.org/en-US/docs/Web/API/PushMessageData.
    const eventInfo = event.data.text();
    const data = JSON.parse(eventInfo);
    const head = data.head || 'New Notification 🕺🕺';
    const body = data.body || 'This is default content. Your notification didn\'t have one 🙄🙄';

    // Keep the service worker alive until the notification is created.
    event.waitUntil(
        self.registration.showNotification(head, {
            body: body,
            icon: 'https://i.imgur.com/MZM3K5w.png'
        })
    );
});
