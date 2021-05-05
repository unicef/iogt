function interceptClickEvent(event: MouseEvent, element: HTMLElement) {
    if (element.tagName === 'A') {
        const href = element.getAttribute('href');
        console.log("HREF ", href)
        //put your logic here...
        if (true) {
           // event.preventDefault();
        }
    }
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