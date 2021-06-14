importScripts('https://storage.googleapis.com/workbox-cdn/releases/6.1.5/workbox-sw.js');

// The below implementation will basically convert "{{ test_url }}" which is test/ into http://localhost:8000/test
// The relative paths such as test/ of the pages inside the app will be provided by the backend devs, 
// so this will be done programmatically

const appShell = [
  "{{ test_url }}"
].map((partialUrl) => `${location.protocol}//${location.host}${partialUrl}`);

workbox.precaching.precacheAndRoute(appShell.map(url => ({
  url,
  revision: null,
})));

