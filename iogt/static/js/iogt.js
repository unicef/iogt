function interceptClickEvent(event, element) {
    if (element.tagName === 'A') {
        if (isIOGTLink(element)) {
            console.log(element, " is an IOGT link element");
            event.preventDefault();
            fetchPageHTML(element.href, function (resText) {
                const nextPageElem = document.createElement("html");
                nextPageElem.innerHTML = resText;
                const title = nextPageElem.getElementsByTagName("title")[0].innerText.trim();
                document.title = title;
                if (window.history.pushState) {
                    window.history.pushState({ "html": resText, "pageTitle": title }, "", element.pathname);
                }
                var newContentElem = nextPageElem.getElementsByClassName("content")[0];
                document.getElementById("content").innerHTML = newContentElem.innerHTML;

                // Add CSS files that are not already in head
                const existingLinkTags = document.getElementsByTagName("link");
                const cssMap = {};
                for (var i = 0; i < existingLinkTags.length; i++) {
                    cssMap[existingLinkTags[i].href] = true;
                }
                const newLinkTags = nextPageElem.getElementsByTagName("link");
                for (var i = 0; i < newLinkTags.length; i++) {
                    const newTag = newLinkTags[i];
                    if (!cssMap[newTag.href]) {
                        document.head.appendChild(newTag);
                    }
                }
            });
        }
    }
}
if (window.history.replaceState) {
    var html = document.getElementById("content").innerHTML;
    var title = document.getElementsByTagName("title")[0].innerText.trim();
    window.history.replaceState({ "html": html, "pageTitle": title }, title);
}
// Ensure navigation through pages that were loaded by XHR still works
window.onpopstate = function (e) {
    if (e.state) {
        document.getElementById("content").innerHTML = e.state.html;
        document.title = e.state.pageTitle;
    }
};
function isIOGTLink(element) {
    if (element.hostname) {
        var iogtHostnames = ["127.0.0.1", "localhost", "goodinternet.org"];
        for (var i = 0; i < iogtHostnames.length; i++) {
            if (element.hostname.indexOf(iogtHostnames[i]) > -1) {
                return true;
            }
        }
        return false;
    }
    return true;
}
function fetchPageHTML(url, callback) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            // Typical action to be performed when the document is ready:
            callback(xhttp.responseText);
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}
//listen for link click events at the document level
if (document.addEventListener) {
    document.addEventListener('click', function (e) {
        interceptClickEvent(e, e.target);
    });
}
else if (document["attachEvent"]) {
    document["attachEvent"]('onclick', function (e) {
        interceptClickEvent(e, e.target || e.srcElement);
    });
}
