document.addEventListener("DOMContentLoaded", function(){
    const handle_help_text = document.querySelector("li.required.slug_field p.help")
    handle_help_text.innerText =
        'The handle must be written in the format "[language_code]_menu_live", ' +
        'e.g. "en_menu_live", for the menu to be live on the website. ' +
        'You can use other handles, e.g. "en_oldmenu", to store other draft ' +
        'menus without them getting displayed.'

    const custom_url_help_text = document.querySelector('#id_iogt_flat_menu_items-0-link_url').parentElement.nextElementSibling
    custom_url_help_text.innerText = 'If you are linking back to a URL on your own IoGT site, ' +
        'be sure to remove the domain and everything before it. ' +
        'For example \'http://sd.goodinternet.org/url/\' ' +
        'should instead be \'/url/\'.'
    custom_url_help_text.style.color = 'red'
});

