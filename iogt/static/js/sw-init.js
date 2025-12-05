const syncStoredRequests = async () => {
  const requests = await getAllRequests();  // IndexedDB fetch

  for (const req of requests) {
    try {
      const headers = new Headers(req.headers);
      const response = await fetch(req.url, {
        method: req.method,
        headers,
        body: req.body,
        credentials: 'include'
      });

      if (response.ok) {
        await deleteRequest(req.id);
        showToast(`✅ Synced back offline filled form.`, "success");
      }
    } catch (err) {
      console.warn("❌ Failed to sync request:", req.url, err);
      showToast(`⚠️ Offline form sync failed for: ${req.url}`, "error");
    }
  }
}

const registerSW = async () => {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});

            const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
            if (!isPushNotificationRegistered) {
                if (isAuthenticated && pushNotification) {
                    registerPushNotification(registration);
                }
            }
        } catch (error) {
            console.error("❌ Service worker registration failed:", error);
        }
    }
};

registerSW();

// Flip "Download available" -> "✓ Available offline" if the target is cached
(async function markCachedSections() {
  if (!('caches' in window)) return;

  const badges = Array.from(document.querySelectorAll('.offline-badge[data-mode="download"]'));
  if (!badges.length) return;

  function absURL(urlStr) {
    const u = new URL(urlStr, window.location.origin);
    u.hash = '';
    return u.toString();
  }

  async function isPageCached(urlStr) {
    const cache = await caches.open('iogt');
    const res = await cache.match(absURL(urlStr));
    if (!res) return false;
    const ct = res.headers.get('Content-Type') || '';
    return ct.includes('text/html');
  }

  async function refresh() {
    await Promise.all(badges.map(async (badge) => {
      const url = badge.getAttribute('data-url');
      const cached = await isPageCached(url);
      if (cached) {
        badge.classList.add('is-cached');
        badge.textContent = '✓ Available offline';
      } else {
        badge.classList.remove('is-cached');
        badge.textContent = '⬇ Download available';
      }
    }));
  }

  await refresh();
  window.addEventListener('online', refresh);
  window.addEventListener('offline', refresh);
  navigator.serviceWorker?.addEventListener?.('message', (e) => {
    if (e.data?.type === 'WARM_CACHE_DONE') refresh();
  });
})();





function getItem (key, defaultValue = null) {
    try {
        return JSON.parse(localStorage.getItem(key)) ?? defaultValue;
    } catch {
        return defaultValue;
    }
};

window.addEventListener('online', () => {
    console.log("🌐 Back online. Trying to sync stored requests...");
    syncStoredRequests();
    enableForOnlineAccess();
  });
