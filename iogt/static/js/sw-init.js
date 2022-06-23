if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'})
        .then(registration => {
            if (registration.installing) {
                console.log('Service worker installing.');
            } else if (registration.waiting) {
                console.log('Service worker installed.');
            } else if (registration.active) {
                console.log('Service worker active.');
            }
            const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
            if (!isPushNotificationRegistered) {
                console.log('Push notification not registered.')
                registerPushNotification(registration);
            } else {
                console.log('Push notification already registered.')
            }
        })
        .catch(error => {
            console.log('Error while registering service worker.', error);
        });
} else {
    console.log('Service worker not supported.');
}
