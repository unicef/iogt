async function registerPushSW() {
    const pushPlus = getItem('pushPlus', false);
    const pushRegistered = getItem('pushRegistered', false);
    if (!pushPlus) {
        if ('serviceWorker' in navigator) {
            const reg = await navigator.serviceWorker.register(pushSWURL, {scope: '/'});
            if (!pushRegistered) {
                initialiseState(reg);
            }
        } else {
            alert("You can't send push notifications.");
        }
    }
}

registerPushSW();
