const registerSW = async () => {
    if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
        const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
        if (!isPushNotificationRegistered) {
            console.log('Push notification not registered.')
            registerPushNotification(registration);
        } else {
            console.log('Push notification already registered.')
        }
    }
};

registerSW();
