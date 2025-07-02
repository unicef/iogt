$(document).ready(() => {
    const externalLinkOverlay = $('#external-link-overlay');
    externalLinkOverlay.click(() => externalLinkOverlay.css('display', 'none'));

    const submitWhenOffline = gettext('You cannot submit when offline');

    const searchFormHolder = $('.search-form-holder');
    const readContent = $('.complete');
    const commentForm = $('.comments__form');
    const commentLikeHolders = $('.like-holder');
    const reportComment = $('.report-comment');
    const commentReplyLinks = $('.reply-link');
    const downloadAppBtns = $('.download-app-btn');
    const offlineAppBtns = $('.offline-app-btn');
    const chatbotBtns = $('.chatbot-btn');
    const questionnaireSubmitBtns = $('.questionnaire-submit-btn');
    const progressHolder = $('.progress-holder');
    const changeDigitalPinBtn = $('.change-digital-pin');
    const loginCreateAccountBtns = $('.login-create-account-btn');
    const logoutBtn = $('.logout-btn');
    const externalLinks = $('a[href*="/external-link/?next="]');

    questionnaireSubmitBtns.each((index, btn) => {
        const $btn = $(btn);
        const span = $btn.find('span');
        if (!span.attr('data-original-label')) {
            span.attr('data-original-label', span.text().trim());
        }
    });

    const disableForOfflineAccess = () => {
        searchFormHolder.hide();
        readContent.removeClass('complete');
        commentForm.hide();
        commentLikeHolders.attr('style', 'display: none !important');
        reportComment.hide();
        commentReplyLinks.hide();
        downloadAppBtns.hide();
        offlineAppBtns.show();
        chatbotBtns.each((index, btn) => {
            const $btn = $(btn);
            $btn.css('pointer-events', 'none');
            $btn.css('background', '#808080');
        });
        questionnaireSubmitBtns.each((index, btn) => {
            const $btn = $(btn);
            const span = $btn.find('span');
            span.text(span.attr('data-original-label'));  // reset label (no "submit when offline")
        });
        progressHolder.hide();
        changeDigitalPinBtn.hide();
        loginCreateAccountBtns.hide();
        logoutBtn.hide();
        externalLinks.each((index, link) => {
            const $link = $(link);
            if (!$link.data('offline-bound')) {
                $link.on('click.offline', e => {
                    e.preventDefault();
                    externalLinkOverlay.css('display', 'block');
                });
                $link.data('offline-bound', true);
            }
        });
    };

    const enableForOnlineAccess = () => {
        searchFormHolder.show();
        readContent.addClass('complete');
        commentForm.show();
        commentLikeHolders.attr('style', 'display: inline-block !important');
        reportComment.show();
        commentReplyLinks.show();
        downloadAppBtns.show();
        offlineAppBtns.hide();
        chatbotBtns.each((index, btn) => {
            const $btn = $(btn);
            $btn.css('pointer-events', 'all');
            $btn.css('background', '#F7F7F9');
        });
        questionnaireSubmitBtns.each((index, btn) => {
            const $btn = $(btn);
            $btn.css('pointer-events', 'all');
            const span = $btn.find('span');
            const original = span.attr('data-original-label') || span.text().trim();
            span.text(original);
        });
        progressHolder.show();
        changeDigitalPinBtn.show();
        loginCreateAccountBtns.show();
        logoutBtn.show();
        externalLinks.show();
        externalLinks.each((index, link) => {
            $(link).off('click.offline');
        });
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
                top: 20px;
                right: 20px;
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

    $(window).on('offline', () => {
        console.warn("🔌 Offline detected.");
        disableForOfflineAccess();
        if (getItem('offlineReady') === true) {
            console.log("📦 Page cached. Reloading offline view...");
            setTimeout(() => location.reload(), 500);
        }
    });

    $(window).on('online', () => {
        enableForOnlineAccess();
    });

    window.navigator.onLine ? enableForOnlineAccess() : disableForOfflineAccess();

    fetch(window.location.href, { method: 'HEAD', cache: 'no-cache' })
    .then(() => {
            console.log("✅ Verified online via HEAD request");
        enableForOnlineAccess();
    })
    .catch(() => {
            console.warn("⚠️ Verified offline via HEAD request");
        disableForOfflineAccess();
    });

    $('.footer-head').hide();
});

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
            setItem('offlineReady', true); // ✅ Set offline-ready flag
            console.log("✅ Content cached successfully!");
            alert("✅ Content is now available offline!");
            location.reload(); // ✅ Reload after caching
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
    if (!registration.showNotification || Notification.permission === 'denied' || !('PushManager' in window)) {
        return;
    }
    subscribe(registration);
};

const urlB64ToUint8Array = base64String => {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
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

            const vapidKey = $('meta[name="vapid-key"]').attr('content');
            const options = {
                userVisibleOnly: true,
                ...(vapidKey && { applicationServerKey: urlB64ToUint8Array(vapidKey) })
            };

            registration.pushManager.subscribe(options)
                .then(subscription => {
                    sendSubscriptionToServer(subscription, 'subscribe');
                })
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
        headers: {
            'content-type': 'application/json'
        },
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
                if (subscription) {
                    sendSubscriptionToServer(subscription, 'unsubscribe');
                }
            });
        });
    }
};
