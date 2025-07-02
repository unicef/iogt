const ready = (callback) => {
    if (document.readyState !== "loading") callback();
    else document.addEventListener("DOMContentLoaded", callback);
};

const init = () => {
    const show = (el) => el.style.display = '';
    const hide = (el) => el.style.display = 'none';

    const externalLinkOverlay = document.querySelector('#external-link-overlay');
    externalLinkOverlay?.addEventListener('click', (event) => hide(event.target));

    const submitWhenOffline = gettext('You cannot submit when offline');

    const readContent = document.querySelectorAll('.complete');
    const commentLikeHolders = document.querySelectorAll('.like-holder');
    const replyLinks = document.querySelectorAll('.reply-link');
    const offlineAppBtns = document.querySelectorAll('.offline-app-btn');
    const chatbotBtns = document.querySelectorAll('.chatbot-btn');
    const questionnaireSubmitBtns = document.querySelectorAll('.questionnaire-submit-btn');

    // Save original button label
    questionnaireSubmitBtns.forEach(btn => {
        const span = btn.querySelector('span');
        if (span && !span.dataset.originalLabel) {
            span.dataset.originalLabel = span.textContent.trim();
        }
    });

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
    ].flatMap(selector => Array.from(document.querySelectorAll(selector)));

    const blockExternalLinks = (event) => {
        event.preventDefault();
        show(externalLinkOverlay);
    };

    const hideFooterMenu = () => {
        hide(document.querySelector('.footer-head'));
    };

        if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('message', event => {
            const data = event.data;
            if (!data) return;

            switch (data.type) {
                case 'sync-success':
                    showToast(`✅ Synced back offline filled form.`);
                    break;
                case 'sync-failed':
                    showToast(`⚠️ Offline form sync failed for: ${data.url}`, true);
                    break;
                case 'sync-error':
                    showToast(`❌ Sync error: ${data.error}`, true);
                    break;
            }
        });
    }

    // Basic toast implementation
    function showToast(message, isError = false) {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${isError ? '#e74c3c' : '#2ecc71'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            font-size: 14px;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        `;
        document.body.appendChild(toast);
        setTimeout(() => toast.style.opacity = 1, 10);
        setTimeout(() => {
            toast.style.opacity = 0;
            setTimeout(() => document.body.removeChild(toast), 600);
        }, 4000);
    }

    const disableForOfflineAccess = () => {
        elementsToToggle.forEach(hide);
        replyLinks.forEach(hide);
        readContent.forEach(el => el.classList.remove('complete'));
        commentLikeHolders.forEach(el => el.setAttribute('style', 'display:none !important'));
        offlineAppBtns.forEach(show);
        chatbotBtns.forEach(btn => {
            btn.style.pointerEvents = 'none';
            btn.style.background = '#808080';
        });
        questionnaireSubmitBtns.forEach(btn => {
            btn.style.pointerEvents = 'all';  // ensure it's still clickable
            const span = btn.querySelector('span');
            if (span) {
                span.textContent = span.dataset.originalLabel || span.textContent.trim();
            }
        });
        externalLinks.forEach(link => link.addEventListener('click', blockExternalLinks));
    };

    const enableForOnlineAccess = () => {
        elementsToToggle.forEach(show);
        readContent.forEach(el => el.classList.add('complete'));
        commentLikeHolders.forEach(el => el.setAttribute('style', 'display:inline-block !important'));
        replyLinks.forEach(el => el.setAttribute('style', 'display:inline-block'));
        offlineAppBtns.forEach(hide);
        chatbotBtns.forEach(btn => {
            btn.style.pointerEvents = 'all';
            btn.style.background = '#F7F7F9';
        });
        questionnaireSubmitBtns.forEach(btn => {
            btn.style.pointerEvents = 'all';
            const span = btn.querySelector('span');
            if (span) {
                span.textContent = span.dataset.originalLabel || span.textContent.split('(')[0].trim();
            }
        });
        externalLinks.forEach(link => {
            show(link);
            link.removeEventListener('click', blockExternalLinks);
        });
    };

    window.addEventListener('offline', () => {
        console.warn("🔌 Offline detected.");
        disableForOfflineAccess();
        if (getItem('offlineReady') === true) {
            console.log("📦 Page cached. Reloading offline view...");
            setTimeout(() => location.reload(), 3000);
        }
    });

    window.addEventListener('online', enableForOnlineAccess);

    window.navigator.onLine ? enableForOnlineAccess() : disableForOfflineAccess();

    hideFooterMenu();

    // Force re-check of online status
    fetch(window.location.href, { method: 'HEAD', cache: 'no-cache' })
    .then(() => {
            console.log("✅ Verified online via HEAD request");
        enableForOnlineAccess();
    })
    .catch(() => {
            console.warn("⚠️ Verified offline via HEAD request");
        disableForOfflineAccess();
    });
};

const download = pageId => {
    alert("📥 Download starting…");
    console.log("Starting download for page:", pageId);

    fetch(`/page-tree/${pageId}/`)
        .then(resp => {
            if (!resp.ok) {
                throw new Error(`Failed to fetch URLs for caching. Status: ${resp.status}`);
            }
            return resp.json();
        })
        .then(urls => {
            if (!Array.isArray(urls) || urls.length === 0) {
                throw new Error("No URLs received for caching.");
            }

            return caches.open('iogt').then(cache => {
                console.log("URLs to cache:", urls);
                return Promise.all(urls.map(url =>
                    fetch(url, { method: 'HEAD' })
                        .then(response => {
                            if (response.ok) {
                                return cache.add(url).catch(error => {
                                    if (error.name === 'QuotaExceededError') {
                                        alert("⚠️ Your storage limit has been reached! Please free up space.");
                                        throw new Error("Storage full! Cannot cache more content.");
                                    }
                                    throw error;
                                });
                            } else {
                                console.warn(`Skipping invalid URL: ${url} (Status: ${response.status})`);
                            }
                        })
                        .catch(err => console.warn(`Skipping ${url} due to error:`, err))
                ));
            });
        })
        .then(() => {
            setItem('offlineReady', true); // ✅ Mark ready for offline
            console.log("✅ Content cached successfully!");
            alert("✅ Content is now available offline!");
            location.reload();
        })
        .catch(error => {
            console.error("❌ Download error:", error);
            alert("⚠️ Download failed. Please try again.");
        });
};

function getItem (key, defaultValue = null) {
    try {
        return JSON.parse(localStorage.getItem(key)) ?? defaultValue;
    } catch {
        return defaultValue;
    }
};

const setItem = (key, value) => {
    localStorage.setItem(key, JSON.stringify(value));
};

const registerPushNotification = registration => {
    if (!registration.showNotification) return;
    if (Notification.permission === 'denied') return;
    if (!'PushManager' in window) return;
    subscribe(registration);
};

const urlB64ToUint8Array = base64String => {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    return Uint8Array.from([...rawData].map(char => char.charCodeAt(0)));
};

const subscribe = registration => {
    registration.pushManager.getSubscription()
        .then(subscription => {
            if (subscription) {
                sendSubscriptionToServer(subscription, 'subscribe');
                return;
            }
            const vapidKey = document.querySelector('meta[name="vapid-key"]')?.content;
            const options = { userVisibleOnly: true };
            if (vapidKey) options.applicationServerKey = urlB64ToUint8Array(vapidKey);

            registration.pushManager.subscribe(options)
                .then(subscription => sendSubscriptionToServer(subscription, 'subscribe'))
                .catch(error => console.log("Error during subscribe()", error));
        })
        .catch(error => console.log("Error during getSubscription()", error));
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
        headers: { 'content-type': 'application/json' },
        credentials: "include"
    }).then(() => {
        setItem('isPushNotificationRegistered', statusType === 'subscribe');
    });
};

const unSubscribePushNotifications = () => {
    const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
    if (isPushNotificationRegistered && isAuthenticated && 'serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(registration => {
            registration.pushManager.getSubscription().then(subscription => {
                if (subscription) sendSubscriptionToServer(subscription, 'unsubscribe');
            });
        });
    }
};

ready(init);
