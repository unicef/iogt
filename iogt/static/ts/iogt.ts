function interceptClickEvent(event: MouseEvent, element: HTMLAnchorElement) {
    if (element.tagName === 'A') {
        if (isIOGTLink(element)) {
            console.log(element, " is an IOGT link element");
            event.preventDefault();
            
            fetchPageHTML(element.href, (resText) => {
                const nextPageElem = document.createElement("html");
                nextPageElem.innerHTML = resText;
                const title = nextPageElem.getElementsByTagName("title")[0].innerText.trim();
                document.title = title;
                if (window.history.pushState) {
                    window.history.pushState({"html": resText,"pageTitle": title },"", element.pathname);
                }
                const newContentElem = nextPageElem.getElementsByClassName("content")[0];

                // Load CSS Link Tags
                const existingLinkMap = {};
                const existingLinks = document.getElementsByTagName("link");
                for (var i = 0; i < existingLinks.length; i++) {
                    existingLinkMap[existingLinks[i].href] = existingLinks[i];
                }
                const newLinks = nextPageElem.getElementsByTagName("link");
                for (var i = 0; i < newLinks.length; i++) {
                    if (!existingLinkMap[newLinks[i].href]) {
                        document.head.appendChild(newLinks[i]);
                    }
                }
                document.getElementById("content").innerHTML = newContentElem.innerHTML;
            });
        }
    }
}

if (window.history.replaceState) {
    const html = document.getElementById("content").innerHTML;
    const title = document.getElementsByTagName("title")[0].innerText.trim();
    window.history.replaceState({"html": html, "pageTitle": title}, title);
}

// Ensure navigation through pages that were loaded by XHR still works
window.onpopstate = function(e){
    if(e.state){
        document.getElementById("content").innerHTML = e.state.html;
        document.title = e.state.pageTitle;
    }
};

function isIOGTLink(element: HTMLAnchorElement): boolean {
    if (element.hostname) {
        const iogtHostnames = ["127.0.0.1", "localhost", "goodinternet.org"];
        for (var i = 0; i < iogtHostnames.length; i++) {
            if (element.hostname.indexOf(iogtHostnames[i]) > -1) {
                return true;
            }
        }
        return false;
    }
    return true;
}

function fetchPageHTML(url: string, callback: (res: string) => any) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
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
    document.addEventListener('click', function(e: any) {
        interceptClickEvent(e, e.target);
    });
} else if (document["attachEvent"]) { // Support IE < 9
    document["attachEvent"]('onclick', function(e) {
        interceptClickEvent(e, e.target || e.srcElement);
    });
}