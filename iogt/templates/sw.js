importScripts('../static/third_party/workbox/workbox-v6.1.5/workbox-sw.js');

// Below we are using a custom dimension to track online vs. offline interactions. So make
// sure to create a custom dimension on GA

workbox.googleAnalytics.initialize({
  parameterOverrides: {
    cd1: 'offline',
  },
});

// The below implementation will basically convert "{{ test_url }}" which is test/ into http://localhost:8000/test
// The relative paths such as test/ of the pages inside the app will be provided by the backend devs,
// so this will be done programmatically

const appShell = [
  "/youth",
].map((partialUrl) => `${location.protocol}//${location.host}${partialUrl}`);

workbox.precaching.precacheAndRoute(appShell.map(url => ({
  url,
  revision: null,
})));

const successMsg = "Your app is now ready to install. If you are using a iOS device, you can install it by clicking 'Share', scrolling down and tapping 'Add to Home Screen. If using Android choose 'Add to home screen' and you should be all set!";

alert(successMsg)