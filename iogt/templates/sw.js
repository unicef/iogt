// Import Workbox if needed
importScripts('/static/js/workbox/workbox-v6.1.5/workbox-sw.js');

self.addEventListener('install', event => {
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', event => {
    event.waitUntil(self.clients.claim());
});

const languageCodeRegEx = RegExp('^\\/(\\w+([@-]\\w+)?)(\\/|$)');
const CACHE_NAME = 'iogt';

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(response => {
                return caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, response.clone());
                    return response;
                });
            })
            .catch(() => {
                return caches.open(CACHE_NAME).then(cache => {
                    return cache.match(event.request).then(match => {
                        if (match) return match;

                        if (event.request.headers.get('Accept').includes('text/html')) {
                            const lang = languageCodeRegEx.exec(new URL(event.request.url).pathname)?.[1] || 'en';
                            return cache.match(`/${lang}/offline-content-not-found/`);
                        }
                    });
                });
            })
    );
});

// Optional: Push notifications
self.addEventListener('push', event => {
    const { head, body, icon, url } = event.data?.json() || {
        head: "No Content",
        body: "No Content",
        icon: "",
        url: self.location.origin
    };

    event.waitUntil(
        self.registration.showNotification(head, {
            body: body,
            icon: icon,
            data: { url }
        })
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});

// ✅ Background Sync for offline submissions
self.addEventListener('sync', event => {
    if (event.tag === 'sync-offline-data') {
        event.waitUntil(syncOfflineData());
    }
});

// 🧠 IndexedDB helpers
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('offline-submissions', 1);
        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('forms')) {
                db.createObjectStore('forms', { keyPath: 'id', autoIncrement: true });
            }
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function syncOfflineData() {
    const db = await openDB();
    const tx = db.transaction('forms', 'readwrite');
    const store = tx.objectStore('forms');

    const allRecords = await store.getAll();
    for (let record of allRecords) {
        try {
            await fetch('/api/submit/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(record.data)
            });
            await store.delete(record.id);
        } catch (err) {
            console.error('Failed to sync record:', err);
        }
    }
}
