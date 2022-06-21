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
        })
        .catch(error => {
            console.log('Error while registering service worker.', error);
        });
} else {
    console.log('Service worker not supported.');
}
