importScripts('../static/js/workbox/workbox-v6.1.5/workbox-sw.js');

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

self.addEventListener('fetch', function(event) {
  event.respondWith(
    fetch(event.request).catch(function() {
      return caches.match(event.request);
    })
  );
});

// Register event listener for the 'push' event.
self.addEventListener('push', function(event) {
    // Retrieve the textual payload from event.data (a PushMessageData object).
    // Other formats are supported (ArrayBuffer, Blob, JSON), check out the documentation
    // on https://developer.mozilla.org/en-US/docs/Web/API/PushMessageData.
    let payload = event.data ? event.data.text() : {"head": "No Content", "body": "No Content", "icon": ""},
      data = JSON.parse(payload),
      head = data.head,
      body = data.body,
      icon = data.icon;
      // If no url was received, it opens the home page of the website that sent the notification
      // Whitout this, it would open undefined or the service worker file.
      url = data.url ? data.url: self.location.origin;
  
    // Keep the service worker alive until the notification is created.
    event.waitUntil(
      // Show a notification with title 'ServiceWorker Cookbook' and use the payload
      // as the body.
      self.registration.showNotification(head, {
        body: body,
        icon: icon,
        data: {url: url}	
      })
    );
});
  
self.addEventListener('notificationclick', function (event) {
    event.waitUntil(
        event.preventDefault(),
        event.notification.close(),
        self.clients.openWindow(event.notification.data.url)
    );
});
