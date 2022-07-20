if ('serviceWorker' in navigator) {
    await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
    const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
    if (!isPushNotificationRegistered) {
        console.log('Push notification not registered.')
        registerPushNotification(registration);
    } else {
        console.log('Push notification already registered.')
    }
}
