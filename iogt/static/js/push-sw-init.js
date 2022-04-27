async function registerSW() {
    const pushPlus = localStorage.getItem('pushPlus', false);
    if (!pushPlus) {
        if ('serviceWorker' in navigator) {
            const reg = await navigator.serviceWorker.register(pushSWURL);
            initialiseState(reg);
        } else {
            alert("You can't send push notifications.");
        }
    }
}

function initialiseState(reg) {
    if (!reg.showNotification) {
        alert("Showing notifications isn't supported.");
        return
    }
    if (Notification.permission === 'denied') {
        alert('You prevented us from showing notifications.');
        return
    }
    if (!'PushManager' in window) {
        alert("Push isn't allowed in your browser.");
        return
    }
    subscribe(reg);
}

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    const outputData = outputArray.map((output, index) => rawData.charCodeAt(index));

    return outputData;
}

async function subscribe(reg) {
    const subscription = await reg.pushManager.getSubscription();
    if (subscription) {
        sendSubData(subscription);
        return;
    }

    const vapidMeta = document.querySelector('meta[name="vapid-key"]');
    const key = vapidMeta.content;
    const options = {
        userVisibleOnly: true,
        // if key exists, create applicationServerKey property
        ...(key && {applicationServerKey: urlB64ToUint8Array(key)})
    };

    const sub = await reg.pushManager.subscribe(options);
    sendSubData(sub)
};

async function sendSubData(subscription) {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
    const data = {
        status_type: 'subscribe',
        subscription: subscription.toJSON(),
        browser: browser,
    };

    const res = await fetch('/webpush/save_information', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json'
        },
        credentials: "include"
    });
    console.log(res);
};

registerSW();
