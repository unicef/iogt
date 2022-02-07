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

const failMsg = gettext('Sorry, there seems to be an error. Please try again soon.');
const successMsg = gettext("Your app is now ready to install. If using Android, choose 'Add to home screen' and you should be all set! If you are using a iOS device, you can install it by clicking 'Share', scrolling down and tapping 'Add to Home Screen.");

const cache = async () => {
    if ('serviceWorker' in navigator && confirm(gettext("Install this website as an app on your device?")) === true) {
        try {
            await navigator.serviceWorker.register(serviceWorkerURL, {scope: '/'});
            alert(successMsg)
        } catch {
            alert(failMsg);
        }
    }
}


$(document).ready(() => {
    const searchInput = $('.search-input');
    const searchBtn = $('.js-search-btn');
    const commentTextArea = $('#id_comment');
    const postAnonymouslyCheckbox = $('#id_post_anonymously');
    const cannedResponsesDropdown = $('#id_canned_responses');
    const addCannedResponseInput = $('#id_add_canned_response');
    const leaveCommentInput = $('#id_leave_comment');
    const commentReplyBtns = $('.reply-link');
    const commentLikeBtns = $('.comment-like-btn');
    const changeDigitalPinBtns = $('.change-digital-pin');
    const chatbotBtns = $('.chatbot-btn');
    const downloadAppBtns = $('.download-app-btn');
    const questionnaireSubmitBtns = $('.survey-page__btn');
    const progressHolder = $('.progress-holder');

    const disableForOfflineAccess = () => {
        searchInput.each((index, value) => {
            $(value).attr('disabled', true);
        });
        searchBtn.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return false;
            })
        });
        commentTextArea.attr('disabled', true);
        postAnonymouslyCheckbox.attr('disabled', true);
        cannedResponsesDropdown.attr('disabled', true);
        addCannedResponseInput.attr('disabled', true);
        leaveCommentInput.attr('disabled', true);
        commentReplyBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return false;
            });
        });
        commentLikeBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return false;
            });
        });
        changeDigitalPinBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return false;
            });
        });
        chatbotBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return false;
            });
        });
        downloadAppBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return false;
            });
        });
        questionnaireSubmitBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return false;
            });
        });
        progressHolder.hide();
    };

    const enableForOnlineAccess = () => {
        searchInput.each((index, value) => {
            $(value).attr('disabled', false);
        });
        searchBtn.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return true;
            })
        });
        commentTextArea.attr('disabled', false);
        postAnonymouslyCheckbox.attr('disabled', false);
        cannedResponsesDropdown.attr('disabled', false);
        addCannedResponseInput.attr('disabled', false);
        leaveCommentInput.attr('disabled', false);
        commentReplyBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return true;
            });
        });
        commentLikeBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return true;
            });
        });
        changeDigitalPinBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return true;
            });
        });
        chatbotBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                cache();
            });
        });
        downloadAppBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return true;
            });
        });
        questionnaireSubmitBtns.each((index, value) => {
            $(value).unbind();
            $(value).click(() => {
                return true;
            });
        });
        progressHolder.show();
    };

    window.addEventListener('offline', e => {
        disableForOfflineAccess();
    });


    window.addEventListener('online', e => {
        enableForOnlineAccess();
    });

    if (!window.navigator.onLine) {
        disableForOfflineAccess();
    }

    downloadAppBtns.each((index, value) => {
        $(value).unbind();
        $(value).click(() => {
            cache();
        });
    });
});
