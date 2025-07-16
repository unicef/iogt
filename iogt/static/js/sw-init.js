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
        console.log("✅ Synced:", req.url);
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
            console.log('isPushNotificationRegistered', isPushNotificationRegistered)
            if (!isPushNotificationRegistered) {
                if (isAuthenticated && pushNotification) {
                    console.log('sending push not')
                    registerPushNotification(registration);
                }
            }
        } catch (error) {
            console.error("❌ Service worker registration failed:", error);
        }
    }
};

registerSW();

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
