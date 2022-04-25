// Register event listener for the 'push' event.
self.addEventListener('push', function (event) {
    // Retrieve the textual payload from event.data (a PushMessageData object).
    // Other formats are supported (ArrayBuffer, Blob, JSON), check out the documentation
    // on https://developer.mozilla.org/en-US/docs/Web/API/PushMessageData.
    const eventInfo = event.data.text();
    const data = JSON.parse(eventInfo);
    const head = data.head || 'New Notification 🕺🕺';
    const body = data.body || 'This is default content. Your notification didn\'t have one 🙄🙄';

    // Keep the service worker alive until the notification is created.
    event.waitUntil(
        self.registration.showNotification(head, {
            body: body,
            icon: 'https://i.imgur.com/MZM3K5w.png'
        })
    );
});
