function validateFileUpload(fileInput, file_size_threshold) {
    if (!fileInput.files || !fileInput.files[0])
        return true;
    else {
        var file = fileInput.files[0];
        if (file.size >= file_size_threshold)
            return confirm('The file you have uploaded exceeds ' + Math.round(file_size_threshold / 1024 / 1024) + 'mb. ' +
                'This will prohibit access to the file in a low bandwidth setting, may restrict feature phone access, or ' +
                'violate your mobile network operator agreements. To reduce file size, try resizing and compressing your ' +
                'file. Do you want to continue?');
    }

    return true;
}

function validateFreeBasicsFileUpload(fileInput, file_size_threshold) {
    if (!fileInput.files || !fileInput.files[0])
        return true;
    else {
        var file = fileInput.files[0];
        if (file.size >= file_size_threshold)
            alert(`File size exceeds facebook free basics limit (${file_size_threshold / 1024}KB).`);
    }

    return true;
}

$(document).ready(() => {
    const externalLinkOverlay = $('#external-link-overlay')

    externalLinkOverlay.click(() => {
        externalLinkOverlay.css('display', 'none');
    });

    const submitWhenOffline = gettext('You cannot submit when offline');

    const searchFormHolder = $('.search-form-holder');
    const readContent = $('.complete')
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
    const externalLinks = $('a[href*="/external-link/?next="]')

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
            btn = $(btn);
            btn.css('pointer-events', 'none');
            btn.css('background', '#808080');
        });
        questionnaireSubmitBtns.each((index, btn) => {
            btn = $(btn);
            btn.css('pointer-events', 'none');
            const span = btn.find('span')
            span.html(`${span.html()} (${submitWhenOffline})`);
        });
        progressHolder.hide();
        changeDigitalPinBtn.hide();
        loginCreateAccountBtns.hide();
        logoutBtn.hide();
        externalLinks.each((index, link) => {
            link = $(link);
            link.click(e => {
                e.preventDefault();
                externalLinkOverlay.css('display', 'block');
            });
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
            btn = $(btn);
            btn.css('pointer-events', 'all');
            btn.css('background', '#F7F7F9');
        });
        questionnaireSubmitBtns.each((index, btn) => {
            btn = $(btn);
            btn.css('pointer-events', 'all');
            const span = btn.find('span')
            span.html(`${span.html().split(`(${submitWhenOffline})`)[0]}`);
        });
        progressHolder.show();
        changeDigitalPinBtn.show();
        loginCreateAccountBtns.show();
        logoutBtn.show();
        externalLinks.show();
        externalLinks.each((index, link) => {
            link = $(link);
            link.off('click');
        });
    };

    $(window).on('offline', () => disableForOfflineAccess());
    $(window).on('online', () => enableForOnlineAccess());

    window.navigator.onLine ? enableForOnlineAccess() : disableForOfflineAccess();
});

const download = pageId => {
    fetch(`/page-tree/${pageId}/`)
        .then(resp => resp.json())
        .then(urls => {
            caches.open('iogt')
                .then(cache => {
                    cache.addAll(urls);
                });
        })
};

const getItem = (key, defaultValue) => {
    return JSON.parse(localStorage.getItem(key, defaultValue));
};

const setItem = (key, value) => {
    localStorage.setItem(key, JSON.stringify(value));
};

const registerPushNotification = registration => {
    if (!registration.showNotification) {
        console.log("Showing notifications isn't supported.");
        return;
    }
    if (Notification.permission === 'denied') {
        console.log("You prevented us from showing notifications.");
        return;
    }
    if (!'PushManager' in window) {
        console.log("Push isn't allowed in your browser.");
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
}

const subscribe = registration => {
    registration.pushManager.getSubscription()
        .then(subscription => {
            if (subscription) {
                sendSubscriptionToServer(subscription);
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
                    sendSubscriptionToServer(subscription);
                })
                .catch(error => {
                    console.log("Error during subscribe()", error);
                });
        })
        .catch(error => {
            console.log("Error during getSubscription()", error);
        });
};

const sendSubscriptionToServer = subscription => {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
    const data = {
        status_type: 'subscribe',
        subscription: subscription.toJSON(),
        browser: browser,
    };

    console.log('Sending user subscription', data);

    fetch('/webpush/subscribe/', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json'
        },
        credentials: "include"
    }).then(resp => {
        console.log('Successfully saved user subscription', resp.ok);
        setItem('isPushNotificationRegistered', true);
    }).catch(error => {
        console.log('Unable to save user subscription', error);
    });
};


const unsubscribePushNotifications = registration => {
    registration.pushManager.getSubscription()
        .then(subscription => {
            if (subscription) {
                const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
                const data = {
                    status_type: 'unsubscribe',
                    subscription: subscription.toJSON(),
                    browser: browser,
                };

                console.log('Sending user unsubscription', data);

                fetch('/webpush/subscribe/', {
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: {
                        'content-type': 'application/json'
                    },
                    credentials: "include"
                }).then(resp => {
                    console.log('Successfully saved user unsubscription', resp.ok);
                    setItem('isPushNotificationRegistered', false);
                }).catch(error => {
                    console.log('Unable to save user unsubscription', error);
                });
            }
        })
        .catch(error => {
            console.log("Error during getSubscription()", error);
        });
};

const unregisterPushNotifications = async () => {
    const isPushNotificationRegistered = getItem('isPushNotificationRegistered', false);
    if (isPushNotificationRegistered) {
        console.log('Push notification already registered.')
        if (isAuthenticated) {
            if ('serviceWorker' in navigator) {
                const registration = await navigator.serviceWorker.ready;
                unsubscribePushNotifications(registration);
            }
        } else {
            console.log('User isn\'t authenticated.')
        }
    } else {
        console.log('Push notification isn\'t registered.')
    }
};
