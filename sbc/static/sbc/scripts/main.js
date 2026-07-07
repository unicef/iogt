document.addEventListener("DOMContentLoaded", () => {
    const opener = document.querySelector("#sbc-mobile-menu-opener");
    const menu = document.querySelector("#sbc-mobile-menu");
    const overlay = document.querySelector("#sbc-mobile-menu-overlay");

    if (!opener || !menu) return;

    opener.addEventListener("click", () => {
        if (menu.classList.contains("open")) {
            menu.classList.remove("open");
            opener.classList.remove("open");
        } else {
            menu.classList.add("open");
            opener.classList.add("open");
        }
    });

    overlay.addEventListener("click", () => {
        menu.classList.remove("open");
        opener.classList.remove("open");
    })
});
