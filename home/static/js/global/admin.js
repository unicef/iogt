$( document ).ready(function () {
    $("li.required.slug_field p.help").text(
        'The handle must be written in the format "[language_code]_menu_live", ' +
        'e.g. "en_menu_live", for the menu to be live on the website. ' +
        'You can use other handles, e.g. "en_oldmenu", to store other draft ' +
        'menus without them getting displayed.'
    );

    const custom_url_section = $("#id_iogt_flat_menu_items-0-link_url").parent();
    const custom_url_help_text = $("<p class='help'></p>").text(
        'If you are linking back to a URL on your own IoGT site, ' +
        'be sure to remove the domain and everything before it. ' +
        'For example \'http://sd.goodinternet.org/url/\' ' +
        'should instead be \'/url/\'.'
    ).css('color', 'red');
    custom_url_section.append(custom_url_help_text);
});