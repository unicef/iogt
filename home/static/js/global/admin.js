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

    if (window.location.pathname.indexOf('/admin/redirects/') === 0) {
      if (window.location.pathname.indexOf('/admin/redirects/add/') === 0){
        $('#id_is_permanent').removeAttr('checked');
      }
      $('#id_is_permanent').parent().next('p').html('Recommendation: Do not use permanent redirects if you are setting ' +
          'up a promotion, QR code, or similar. Use permanent redirects if you are permanently moving the location of ' +
          'content on your site.<br><strong>Cons:</strong> If you change or even delete a permanent redirect after you create it, the ' +
          'users who already accessed it will still continue to behave as if the original redirect is in place. This is' +
          'because permanent redirects are normally stored by the user\'s browser until they delete their browser cache.' +
          'Your browser may also store the permanent redirect until you clear its cache. <br><strong>Pros:</strong> Permanent redirects' +
          'ensure search engines forget the old page (the \'Redirect from\') and index the new page instead.'
      ).css({'color': 'red'});
    }
});
