const registerSW = async () => {
    if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
        const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
        if (!isPushNotificationRegistered) {
            if (isAuthenticated && pushNotification) {
                registerPushNotification(registration);
            }
        }
    }
};

registerSW();
