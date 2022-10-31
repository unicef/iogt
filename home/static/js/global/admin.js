$(document).ready(function () {
    $('#id_handle').parent().siblings('p[class=help]').text(
        'The handle must be written in the format "[language_code]_menu_live", e.g. "en_menu_live", for the menu to ' +
        'be live on the website. You can use other handles, e.g. "en_oldmenu", to store other draft menus without ' +
        'them getting displayed.'
    ).css({'color': 'red'});

    $('#id_heading').parent().siblings('p[class=help]').replaceWith( $("<a />")
        .attr({"href":"http://127.0.0.1:8000/admin/settings/home/themesettings/", "target":"_blank"})
        .html("Click here to edit the background color for all Flat Menus in Theme Settings."))

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

});
