const ready = (callback) => {
    if (document.readyState != "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
};

const init = (event) => {
    const show = (el) => el.style.display = 'block';
    const hide = (el) => el.style.display = 'none';

    const externalLinkOverlay = document.querySelector('#external-link-overlay');
    externalLinkOverlay.addEventListener('click', (event) => hide(event.target));

    const submitWhenOffline = gettext('You cannot submit when offline');

    const readContent = document.querySelectorAll('.complete');
    const commentLikeHolders = document.querySelectorAll('.like-holder');
    const replyLinks = document.querySelectorAll('.reply-link');
    const offlineAppBtns = document.querySelectorAll('.offline-app-btn');
    const chatbotBtns = document.querySelectorAll('.chatbot-btn');
    const questionnaireSubmitBtns = document.querySelectorAll('.questionnaire-submit-btn');
    const externalLinks = document.querySelectorAll('a[href*="/external-link/?next="]');
    const elementsToToggle = [
        '.download-app-btn',
        '.login-create-account-btn',
        '.change-digital-pin',
        '.comments__form',
        '.logout-btn',
        '.progress-holder',
        '.report-comment',
        '.search-form-holder',
    ].flatMap(
        (selector) => Array.from(document.querySelectorAll(selector))
    );
    console.log(elementsToToggle);

    const blockExternalLinks = (event) => {
        event.preventDefault();
        show(externalLinkOverlay);
    };

    // for JS enabled devices hide double menu
    const hideFooterMenu = () => {
        hide(document.querySelector('.footer-head'));
    };

    const disableForOfflineAccess = (event) => {
        elementsToToggle.forEach(hide);
        replyLinks.forEach(hide)
        readContent.forEach((el) => el.classList.remove('complete'));
        commentLikeHolders.forEach((el) => el.setAttribute('style', 'display:none !important'));
        offlineAppBtns.forEach(show);
        chatbotBtns.forEach((btn) => {
            btn.style['pointer-events'] = 'none';
            btn.style.background = '#808080';
        });
        questionnaireSubmitBtns.forEach((btn) => {
            btn.style['pointer-events'] = 'none';
            const span = btn.querySelector('span');
            span.innerHTML = `${span.innerHTML} (${submitWhenOffline})`;
        });
        externalLinks.forEach((link) => {
            link.addEventListener('click', blockExternalLinks);
        });
    };

    const enableForOnlineAccess = (event) => {
        elementsToToggle.forEach(show);
        readContent.forEach((el) => el.classList.add('complete'));
        commentLikeHolders.forEach((el) => el.setAttribute('style', 'display:inline-block !important'));
        replyLinks.forEach((el) => el.setAttribute('style', 'display:inline-block'));
        offlineAppBtns.forEach(hide);
        chatbotBtns.forEach((btn) => {
            btn.style['pointer-events'] = 'all';
            btn.style.background = '#F7F7F9';
        });
        questionnaireSubmitBtns.forEach((btn) => {
            btn.style['pointer-events'] = 'all';
            const span = btn.querySelector('span');
            span.innerHTML = span.innerHTML.split(`(${submitWhenOffline})`)[0];
        });
        externalLinks.forEach((link) => {
            show(link);
            link.removeEventListener('click', blockExternalLinks);
        });
    };

    window.addEventListener('offline', disableForOfflineAccess);
    window.addEventListener('online',  enableForOnlineAccess);

    window.navigator.onLine ? enableForOnlineAccess() : disableForOfflineAccess();
    hideFooterMenu();

};

const download = pageId => {
    fetch(`/page-tree/${pageId}/`)
        .then(resp => resp.json())
        .then(urls => {
            caches.open('iogt')
                .then(cache => {
                    cache.addAll(urls);
                });
        });
};

const getItem = (key, defaultValue) => {
    return JSON.parse(localStorage.getItem(key, defaultValue));
};

const setItem = (key, value) => {
    localStorage.setItem(key, JSON.stringify(value));
};

const registerPushNotification = registration => {
    if (!registration.showNotification) {
        return;
    }
    if (Notification.permission === 'denied') {
        return;
    }
    if (!'PushManager' in window) {
        return;
    }
    subscribe(registration);
};

const urlB64ToUint8Array = base64String => {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    const outputData = outputArray.map((output, index) => rawData.charCodeAt(index));

    return outputData;
};

const subscribe = registration => {
    registration.pushManager.getSubscription()
        .then(subscription => {
            if (subscription) {
                sendSubscriptionToServer(subscription, 'subscribe');
                return;
            }
            const vapidKeyMeta = document.querySelector('meta[name="vapid-key"]');
            const vapidKey = vapidKeyMeta.content;
            const options = {
                userVisibleOnly: true,
                // if key exists, create applicationServerKey property
                ...(vapidKey && {applicationServerKey: urlB64ToUint8Array(vapidKey)})
            };

            registration.pushManager.subscribe(options)
                .then(subscription => {
                    sendSubscriptionToServer(subscription, 'subscribe');
                })
                .catch(error => {
                    console.log("Error during subscribe()", error);
                });
        })
        .catch(error => {
            console.log("Error during getSubscription()", error);
        });
};

const sendSubscriptionToServer = (subscription, statusType) => {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
    const data = {
        status_type: statusType,
        subscription: subscription.toJSON(),
        browser: browser,
    };

    fetch('/webpush/subscribe/', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json'
        },
        credentials: "include"
    }).then(resp => {
        setItem('isPushNotificationRegistered', statusType === 'subscribe');
    });
};


const unSubscribePushNotifications = () => {
    const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
    if (isPushNotificationRegistered && isAuthenticated && 'serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(registration => {
            registration.pushManager.getSubscription().then(subscription => {
                subscription && sendSubscriptionToServer(subscription, 'unsubscribe');
            });
        });
    }
};

ready(init);
