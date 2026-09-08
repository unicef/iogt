importScripts("../../static/js/workbox/workbox-v6.1.5/workbox-sw.js");
importScripts("../../static/js/idb.js"); // Import IndexedDB helper
const PRECACHE_ASSETS = [
    '/',  // your home page
    '/static/js/iogt.js',
    '/static/js/iogt-no-jquery.js',
    '/static/js/idb.js',
];

// Bypass the service worker for configured paths or patterns.
// Add paths here to exclude them from SW handling (prefix match supported).
const SW_EXCLUDE_PATHS = [
  '/cranky-uncle-game',
];

const OFFLINE_HTML = `
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <title>Offline</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <style>
        body {
          font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          padding: 16px;
          text-align: center;
          background: #ffffff;
          color: #333;
        }
        .box {
          max-width: 480px;
        }
      </style>
    </head>
    <body>
      <div class="box">
        <p>This content will be available when you are online. Please right click and press back to go back.</p>
      </div>
    </body>
  </html>
`;


// ✅ Install Service Worker
self.addEventListener('install', event => {
    console.log("🛠 Service Worker Installing...");
    event.waitUntil(
        caches.open('iogt').then(async cache => {
            for (const asset of PRECACHE_ASSETS) {
                try {
                    const response = await fetch(asset, { method: 'GET' });
                    if (response.ok) {
                        await cache.put(asset, response.clone());
                        console.log(`✅ Cached: ${asset}`);
                    } else {
                        console.warn(`⚠️ Skipped (not OK): ${asset}`);
                    }
                } catch (err) {
                    console.warn(`⚠️ Skipped (fetch failed): ${asset}`, err);
                }
            }
        }).then(() => self.skipWaiting())
    );
});

self.addEventListener("push", function (event) {
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
    icon:
      data.icon || "https://cdn-icons-png.flaticon.com/512/3119/3119338.png",
    data: {
      url: data.url || "/",
      notification_id: data.notification_id || null,
    },
    requireInteraction: true,
  };

  event.waitUntil(self.registration.showNotification(title, options));
});

// ✅ Activate Service Worker
self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("notificationclick", function (event) {
  // Optional: close the notification
  event.notification.close();

  const notificationData = event.notification.data || {};
  const targetUrl = notificationData.url || "/";

  // Track click via fetch to server
  if (notificationData.notification_id) {
    fetch(`/notifications/mark-clicked/${notificationData.notification_id}/`, {
      method: "POST",
      "X-CSRFToken": "{{ csrf_token }}",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    }).catch((err) =>
      console.warn("❌ Failed to log notification click:", err)
    );
  }

  // Focus tab or open new one
  event.waitUntil(
    clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clientList) => {
        for (let client of clientList) {
          if (client.url === targetUrl && "focus" in client) {
            return client.focus();
          }
        }
        return clients.openWindow(targetUrl);
      })
  );
});

// ✅ Handle Fetch Requests
self.addEventListener("fetch", (event) => {
  const { request } = event;

  function isExcluded(req) {
    try {
      const url = new URL(req.url);
      // Only apply exclusions to same-origin requests
      if (url.origin !== self.location.origin) return false;
      const path = url.pathname;
      for (const p of SW_EXCLUDE_PATHS) {
        if (p.endsWith('*')) {
          const prefix = p.slice(0, -1);
          if (path.startsWith(prefix)) return true;
        } else {
          if (path === p || path.startsWith(p + '/')) return true;
          // Also allow the exclusion fragment to appear anywhere in the path
          // e.g. "/en/.../cranky-uncle-game/..." should match "/cranky-uncle-game"
          if (path.indexOf(p) !== -1) return true;
        }
      }
    } catch (e) {
      return false;
    }
    return false;
  }

  if (isExcluded(request)) {
    // Let these requests go to network directly and skip SW caching/handling.
    return event.respondWith(fetch(request));
  }

  // ✅ Handle POST Requests (Save to IndexedDB if offline)
  if (request.method === "POST") {
    event.respondWith(
      fetch(request.clone()).catch(async () => {
        console.warn("⚠️ Offline - saving request locally", request.url);

        try {
          await saveRequest(request);

          if ("sync" in self.registration) {
            self.registration.sync
              .register("sync-forms")
              .then(() => console.log("🔄 Sync registered successfully!"))
              .catch((err) =>
                console.error("❌ Sync registration failed:", err)
              );
          }

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
    if (request.method === 'GET') {
        const reqClone = request.clone();
                event.respondWith(
            fetch(reqClone, { cache: 'no-store' })      // 1️⃣ Try the network first
                .then(networkResponse => {
                    // 2️⃣ Optionally save a copy for offline use
                    const responseClone = networkResponse.clone(); // ✅ Clone early
                    const cacheRequest = new Request(request.url, { method: 'GET' });
                    //    Only cache successful, basic (same‑origin) responses
                    if (networkResponse.ok && networkResponse.type === 'basic' && request.method === 'GET') {
                        caches.open('iogt')
                            .then(cache => cache.put(cacheRequest, responseClone))
                            .catch(err => console.warn('❌ Cache put failed', err));
                    }
                    return networkResponse;                     // 3️⃣ Always return the live response
                })
                .catch(() => { // 4️⃣ Network failed → offline fallback
                return caches.match(request).then(cached => {
                    if (cached) return cached;

                    if (request.mode === 'navigate' || request.destination === 'document') {
                        return new Response(OFFLINE_HTML, {
                            status: 503,
                            headers: { 'Content-Type': 'text/html; charset=utf-8' },
                        });
                    }

                    return new Response('', { status: 503 });
                });
            })
                {% comment %} .catch(() => {                                  // 4️⃣ Network failed → offline fallback
                    return caches.match(request)                //    • Serve from cache if we have it
                        .then(cached => cached ||            //    • …otherwise show a 503
                            new Response('Offline', { status: 503 }));
                }) {% endcomment %}
        );
        
        //Commented - Changed order to check if online -> send request to server -> save in cache -> but if offline -> then check cache
        // event.respondWith(
        //     caches.match(request).then(cachedResponse => {
        //         if (cachedResponse) {
        //             console.log("✅ Serving from cache:", request.url);
        //             return cachedResponse;
        //         }

        //         return fetch(request)
        //             .then(networkResponse => {
        //                 return caches.open('iogt').then(cache => {
        //                     cache.put(reqClone, networkResponse.clone());
        //                     return networkResponse;
        //                 });
        //             })
        //             .catch(err => {
        //                 console.error("❌ Network fetch failed:", request.url, err);
        //                 return new Response('Offline - No cached content available', {
        //                     status: 503,
        //                     headers: { 'Content-Type': 'text/plain' }
        //                 });
        //             });
        //     })
        // );
    }
});

// ✅ Background Sync for Form Submissions
self.addEventListener("sync", (event) => {
  if (event.tag === "sync-forms") {
    event.waitUntil(syncRequests());
  }
});

// ✅ Function to Sync Requests from IndexedDB
async function syncRequests() {
  const requests = await getAllRequests();
  for (const req of requests) {
    console.log("📤 Syncing request:", req);

        const fetchOptions = {
            method: req.method,
            headers: req.headers,
            body: req.body,
            credentials: 'include'  // Important for authentication
        };

    try {
      const response = await fetch(req.url, fetchOptions);

      if (response.ok) {
        await deleteRequest(req.id);
        // ✅ Notify client about successful sync
        sendMessageToClients({ type: "sync-success", url: req.url });
      } else {
        console.warn("⚠️ Sync failed with status:", response.status);
        sendMessageToClients({
          type: "sync-failed",
          url: req.url,
          status: response.status,
        });
      }
    } catch (err) {
      console.error("❌ Sync error:", err);
      sendMessageToClients({
        type: "sync-error",
        url: req.url,
        error: err.message,
      });
    }
  }
}

function sendMessageToClients(message) {
  self.clients
    .matchAll({ includeUncontrolled: true, type: "window" })
    .then((clients) => {
      clients.forEach((client) => {
        client.postMessage(message);
      });
    });
}
