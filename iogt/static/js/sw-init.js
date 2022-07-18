if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
}
