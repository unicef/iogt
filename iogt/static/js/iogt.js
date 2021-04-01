function interceptClickEvent(event, element) {
    if (element.tagName === 'A') {
        if (isIOGTLink(element)) {
            console.log(element, " is an IOGT link element");
            event.preventDefault();
            fetchPageHTML(element.href, function (resText) {
                var nextPageElem = document.createElement("html");
                nextPageElem.innerHTML = resText;
                var title = nextPageElem.getElementsByTagName("title")[0].innerText.trim();
                if (window.history.pushState) {
                    window.history.pushState({ "html": resText, "pageTitle": title }, "", element.pathname);
                }
                transitionToPage(nextPageElem);
            });
        }
    }
}
if (window.history.replaceState) {
    var html = document.documentElement.innerHTML;
    var title = document.getElementsByTagName("title")[0].innerText.trim();
    window.history.replaceState({ "html": html, "pageTitle": title }, title);
}
// Ensure navigation through pages that were loaded by XHR still works
window.onpopstate = function (e) {
    if (e.state) {
        var nextPageElem = document.createElement("html");
        nextPageElem.innerHTML = e.state.html;
        transitionToPage(nextPageElem);
        document.title = e.state.pageTitle;
    }
};
function transitionToPage(nextPageElem) {
    var newContentElem = nextPageElem.getElementsByClassName("content")[0];
    // Load CSS Link Tags
    var existingLinkMap = {};
    var existingLinks = document.getElementsByTagName("link");
    for (var i = 0; i < existingLinks.length; i++) {
        existingLinkMap[existingLinks[i].href] = existingLinks[i];
    }
    var newLinks = nextPageElem.getElementsByTagName("link");
    for (var i = 0; i < newLinks.length; i++) {
        if (!existingLinkMap[newLinks[i].href]) {
            document.head.appendChild(newLinks[i]);
        }
    }
    document.getElementById("new-content").innerHTML = newContentElem.innerHTML;
    document.getElementById("new-content").classList.remove("hide");
    document.getElementById("new-content").classList.add("slide-in");
    setTimeout(function () {
        document.getElementById("content").innerHTML = newContentElem.innerHTML;
        document.getElementById("new-content").classList.add("fade-out");
        document.getElementById("new-content").classList.remove("slide-in");
    }, 310);
    setTimeout(function () {
        document.getElementById("new-content").classList.add("hide");
        document.getElementById("new-content").innerHTML = "";
    }, 620);
}
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
