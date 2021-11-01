document.addEventListener("DOMContentLoaded", function(){
    var handle_help_text = document.querySelector("li.required.slug_field p.help")
    handle_help_text.innerText = 'The handle must be written in the format "[language_code]_menu_live", ' +
            'e.g. "en_menu_live", for the menu to be live on the website. ' +
            'You can use other handles, e.g. "en_oldmenu", to store other draft ' +
            'menus without them getting displayed.'


});


