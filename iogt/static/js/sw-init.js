const registerSW = async () => {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        try {
            const registration = await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});

            // Register background sync event
            const syncTags = await registration.sync.getTags();
            if (!syncTags.includes('sync-forms')) {
                await registration.sync.register('sync-forms');
                console.log("✅ Background sync registered for offline forms!");
            }

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

navigator.serviceWorker.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'ALERT_MESSAGE') {
        alert(event.data.message); // ✅ Show alert when offline
    }
});
