const registerSW = async () => {
    if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
        const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
        if (!isPushNotificationRegistered) {
            if (isAuthenticated) {
                // disable push notification subscription for now
                // for reference see issue https://github.com/unicef/iogt/issues/1388
                // registerPushNotification(registration);
            }
        }
    }
};

registerSW();
