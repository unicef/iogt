// const failMsg = gettext('Sorry, there seems to be an error. Please try again soon.');
// const successMsg = gettext("Your app is now ready to install. If using Android, choose 'Add to home screen' and you should be all set! If you are using a iOS device, you can install it by clicking 'Share', scrolling down and tapping 'Add to Home Screen.");
//
// const cache = async () => {
//     if ('serviceWorker' in navigator && confirm(gettext("Install this website as an app on your device?")) === true) {
//         try {
//             await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
//             alert(successMsg)
//         } catch {
//             alert(failMsg);
//         }
//     }
// }

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
