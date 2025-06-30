importScripts('../../static/js/workbox/workbox-v6.1.5/workbox-sw.js');
importScripts('../../static/js/idb.js');  // Import IndexedDB helper

// ✅ Install Service Worker
self.addEventListener('install', event => {
    console.log("🛠 Service Worker Installing...");
    event.waitUntil(self.skipWaiting());
});

// ✅ Activate Service Worker
self.addEventListener('activate', event => {
    console.log("🚀 Service Workr Activated!");
    event.waitUntil(self.clients.claim());
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

                    // ✅ Dynamically use referrer or fallback to home page
                    const redirectUrl = request.referrer || '/';
                    
                    return new Response(`
                        <!DOCTYPE html>
                        <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>Offline Submission</title>
                                <style>
                                    body { font-family: sans-serif; text-align: center; padding: 50px; }
                                    button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
                                </style>
                            </head>
                            <body>
                                <h2>Your survey will be submitted automatically when you come online.</h2>
                                <button onclick="window.location.href='${redirectUrl}'">Back to Survey</button>
                            </body>
                        </html>
                    `, {
                        headers: { "Content-Type": "text/html" }
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
                        if (request.method === 'GET') {
                            cache.put(request, networkResponse.clone());
                        }
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