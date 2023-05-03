$(document).ready(function () {
    $('#id_handle').parent().siblings('p[class=help]').text(
        'The handle must be written in the format "[language_code]_menu_live", e.g. "en_menu_live", for the menu to ' +
        'be live on the website. You can use other handles, e.g. "en_oldmenu", to store other draft menus without ' +
        'them getting displayed.'
    ).css({'color': 'red'});

    $('#tab-content:contains("Download PO file and input translations offline")')
        .find('>:first-child')
        .prepend('<p style="margin-left: 50px; color: red; font-weight: bold;">' +
            'Use the "STOP TRANSLATION" option if you want to translate additional fields ' +
            'such as: survey/poll/quiz answers, index page description, recommended content, ' +
            'search engine friendly title, search description, lead image, icon.' +
            '</p>')

    $('.transfer.list-container:last + div')
        .prepend('<h4 style="color: #FF0000; font-weight: bold; margin: 5px;">We strongly recommend choosing a ' +
            'destination within the sandbox, to allow checking the transferred content for errors before going ' +
            'live. You can then move the content to the desired final destination.</h4>')

    $('#id_page_permissions-ADD').parent().prepend('<h4 style="color: #FF0000; font-weight: bold; margin: 5px;">' +
        'Giving a Group the EDIT permission will also allow them to download data for Polls, Surveys, and Quizzes ' +
        'for the Pages they can access.</h4>')

    $('#id_seo_title').parent().siblings('p[class=help]').text(
        'The name of the page displayed on search engine results as the clickable headline, and automatically loaded ' +
        'as a title into shares on social media eg Facebook Posts or shared links in WhatsApp.'
    );

    $('#id_search_description').parent().siblings('p[class=help]').text(
        'The descriptive text displayed underneath a headline in search engine results, and automatically loaded ' +
        'as a description into shares on social media eg Facebook Posts or shared links in WhatsApp.'
    );
});

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
