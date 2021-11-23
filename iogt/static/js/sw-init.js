const failMsg = gettext('Something went wrong. Can you try refreshing the page, and clicking the download website button?');
const successMsg = gettext("Your app is now ready to install. If you are using a iOS device, you can install it by clicking 'Share', scrolling down and tapping 'Add to Home Screen. If using Android choose 'Add to home screen' and you should be all set!");

async function cache() {
    if ('serviceWorker' in navigator && confirm(gettext("Install this website as an app on your device?")) === true) {
        try {
            await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
            alert(successMsg)
        } catch {
            alert(failMsg);
        }
    }
}
