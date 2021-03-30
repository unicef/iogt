function interceptClickEvent(event, element) {
    if (element.tagName === 'A') {
        var href = element.getAttribute('href');
        console.log("HREF ", href);
        //put your logic here...
        if (true) {
        }
    }
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
