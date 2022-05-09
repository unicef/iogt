const failMsg = gettext('Sorry, there seems to be an error. Please try again soon.');
const successMsg = gettext("Your app is now ready to install. If using Android, choose 'Add to home screen' and you should be all set! If you are using a iOS device, you can install it by clicking 'Share', scrolling down and tapping 'Add to Home Screen.");

function registerSW() {
    const pushPlus = getItem('pushPlus', false);
    const pushRegistered = getItem('pushRegistered', false);
    if (pushPlus) {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', async () => {
                const reg = await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
                if (!pushRegistered) {
                    initialiseState(reg);
                }
            });
        }
    }
}

const cache = async () => {
    if ('serviceWorker' in navigator && confirm(gettext("Install this website as an app on your device?"))) {
        try {
            await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
            setItem('pushPlus', true);
            alert(successMsg)
        } catch {
            alert(failMsg);
        }
    }
}

registerSW();
