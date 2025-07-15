importScripts('../../static/js/workbox/workbox-v6.1.5/workbox-sw.js');
importScripts('../../static/js/idb.js');  // Import IndexedDB helper

// ✅ Install Service Worker
self.addEventListener('install', event => {
    console.log("🛠 Service Worker Installing...");
    event.waitUntil(self.skipWaiting());
});

self.addEventListener('push', function(event) {
    console.log('📩 Push received', event);

    let data = {};

    try {
        if (event.data && event.data.json) {
            // Try to parse JSON
            data = event.data.json();
        } else if (event.data && event.data.text) {
            // Fallback to text and wrap in object
            const text = event.data.text();
            data = { body: text };
        }
    } catch (e) {
        console.warn("❌ Failed to parse push data", e);
        data = { body: "You have a new message." };
    }

    const title = data.title || "New Notification";
    const options = {
        body: data.body || "You have a new message.",
        icon: data.icon || "https://cdn-icons-png.flaticon.com/512/3119/3119338.png",
        data: {
            url: data.url || '/',
            notification_id: data.notification_id || null,
        },
        requireInteraction: true
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});



// ✅ Activate Service Worker
self.addEventListener('activate', event => {
    console.log("🚀 Service Workr Activated!");
    event.waitUntil(self.clients.claim());
});

self.addEventListener('notificationclick', function(event) {
    console.log('🔔 Notification clicked:', event);

    // Optional: close the notification
    event.notification.close();

    const notificationData = event.notification.data || {};
    const targetUrl = notificationData.url || '/';

    // Track click via fetch to server
    if (notificationData.notification_id) {
        fetch(`/notifications/mark-clicked/${notificationData.notification_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        }).catch(err => console.warn('❌ Failed to log notification click:', err));
    }

    // Focus tab or open new one
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
            for (let client of clientList) {
                if (client.url === targetUrl && 'focus' in client) {
                    return client.focus();
                }
            }
            return clients.openWindow(targetUrl);
        })
    );
});

// ✅ Handle Fetch Requests
self.addEventListener('fetch', event => {
    const { request } = event;

    console.log("🔎 Fetch event triggered:", request.url, request.method);

    // ✅ Handle POST Requests (Store in IndexedDB if Offline)
    if (request.method === 'POST') {
        event.respondWith(
            fetch(request.clone()).catch(async () => {
                console.warn("⚠️ Offline - saving request locally", request.url);

                try {
                    await saveRequest(request);
                    console.log("💾 Request saved successfully:", request.url);

                    // ✅ Register background sync safely
                    self.registration.sync.register('sync-forms')
                        .then(() => console.log("🔄 Sync registered successfully!"))
                        .catch(err => console.error("❌ Sync registration failed:", err));

                    return new Response("Your survey will be submitted automatically when you come online.", {
                        headers: { "Content-Type": "text/plain" }
                    });
                } catch (err) {
                    console.error("❌ Failed to save request:", err);
                    return new Response(JSON.stringify({ success: false, error: err.message }), {
                        headers: { "Content-Type": "application/json" }
                    });
                }
            })
        );
        return;
    }

    // ✅ Handle GET Requests (Serve from Cache when Offline)
    event.respondWith(
        caches.match(request).then(cachedResponse => {
            if (cachedResponse) {
                console.log("✅ Serving from cache:", request.url);
                return cachedResponse;
            }

            return fetch(request)
                .then(networkResponse => {
                    return caches.open('iogt').then(cache => {
                        cache.put(request, networkResponse.clone());
                        return networkResponse;
                    });
                })
                .catch(() => {
                    return new Response('Offline - No cached content available', { status: 503 });
                });
        })
    );
});

// ✅ Background Sync for Form Submissions
self.addEventListener('sync', event => {
    if (event.tag === 'sync-forms') {
        console.log("🔄 Sync event triggered!");
        event.waitUntil(syncRequests());
    }
});

// ✅ Function to Sync Requests from IndexedDB
async function syncRequests() {
    console.log("🚀 Syncing stored requests...");

    const requests = await getAllRequests();
    for (const req of requests) {
        console.log("📤 Syncing request:", req);

        const fetchOptions = {
           method: req.method,
           headers: req.headers,
           body: req.body,
           credentials: 'include'  // Important for authentication
        };

        const response = await fetch(req.url, fetchOptions);

        if (response.ok) {
            console.log("✅ Sync successful, deleting request from IndexedDB...");
            await deleteRequest(req.id);
        } else {
            console.warn("⚠️ Sync failed with status:", response.status);
        }
    }
}