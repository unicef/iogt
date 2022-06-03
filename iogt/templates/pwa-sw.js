self.addEventListener('install', event => {
    console.log('Service worker installed.');
});

self.addEventListener('activate', event => {
    console.log('Service worker activated.');
});

self.addEventListener('fetch', event => {
    console.log(`Responding to ${event.request.url}`);
    event.respondWith(fetch(event.request));
});
