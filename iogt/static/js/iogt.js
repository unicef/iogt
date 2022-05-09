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
    const submitWhenOffline = gettext('You cannot submit when offline');

    const searchFormHolder = $('.search-form-holder');
    const readContent = $('.complete')
    const commentForm = $('.comments__form');
    const commentLikeHolders = $('.like-holder');
    const reportComment = $('.report-comment');
    const commentReplyLinks = $('.reply-link');
    const downloadAppBtns = $('.block-offline_app_button .download-app-btn');
    const offlineAppBtns = $('.block-offline_app_button .offline-app-btn');
    const chatbotBtns = $('.chatbot-btn');
    const questionnaireSubmitBtns = $('.questionnaire-submit-btn');
    const progressHolder = $('.progress-holder');
    const changeDigitalPinBtn = $('.change-digital-pin');
    const loginCreateAccountBtns = $('.login-create-account-btn');
    const logoutBtn = $('.logout-btn');

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
    };

    const isPWA = () => {
        return ["fullscreen", "standalone", "minimal-ui"].some(
            displayMode => window.matchMedia(`(display-mode: ${displayMode})`).matches
        );
    };

    if (isPWA()) {
        $(window).on('offline', () => disableForOfflineAccess());
        $(window).on('online', () => enableForOnlineAccess());

        window.navigator.onLine ? enableForOnlineAccess() : disableForOfflineAccess();
    } else {
        offlineAppBtns.hide();
    }
});

const getItem = (key, defaultValue) => {
    return JSON.parse(localStorage.getItem(key, defaultValue));
};

const setItem = (key, value) => {
    localStorage.setItem(key, JSON.stringify(value));
};

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
}

async function sendSubData(subscription) {
    const browser = navigator.userAgent.match(/(firefox|msie|chrome|safari|trident)/ig)[0].toLowerCase();
    const data = {
        status_type: 'subscribe',
        subscription: subscription.toJSON(),
        browser: browser,
    };

    await fetch('/webpush/save_information', {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'content-type': 'application/json'
        },
        credentials: "include"
    });
    setItem('pushRegistered', true);
}