(function () {
  'use strict';
  var cfg = document.getElementById('copy-page-url-config');
  if (!cfg) return;
  var endpoint = JSON.parse(cfg.textContent);

  function readable(url) {
    try { return decodeURI(url); } catch (e) { return url; }
  }

  function fallbackCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    var ok = document.execCommand('copy');
    document.body.removeChild(ta);
    if (!ok) throw new Error('Copy failed');
  }

  function fetchUrl(pageId) {
    return fetch(endpoint + '?page_id=' + pageId, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' }
    })
      .then(function (r) {
        if (!r.ok) throw new Error('Could not copy');
        return r.json();
      })
      .then(function (d) {
        if (!d.url) throw new Error(d.message || 'No public URL');
        return readable(d.url);
      });
  }

  // ClipboardItem with a promise keeps Safari happy after an async fetch.
  function copy(textPromise) {
    if (window.ClipboardItem && navigator.clipboard && navigator.clipboard.write) {
      var blob = textPromise.then(function (t) {
        return new Blob([t], { type: 'text/plain' });
      });
      return navigator.clipboard.write([new ClipboardItem({ 'text/plain': blob })]);
    }
    return textPromise.then(function (t) {
      if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(t);
      }
      fallbackCopy(t);
    });
  }

  function init() {
    var match = window.location.pathname.match(/\/pages\/(\d+)\/edit\/?$/);
    var slug = document.getElementById('id_slug');
    if (!match || !slug || document.getElementById('copy-page-url-btn')) return;

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'copy-page-url-btn';
    btn.className = 'button button-small button-secondary';
    btn.textContent = 'Copy URL';

    var wrap = slug.parentNode;
    wrap.style.display = 'flex';
    wrap.style.alignItems = 'center';
    wrap.style.gap = '0.5rem';
    slug.style.flex = '1';
    slug.after(btn);

    var timer;
    function flash(msg) {
      btn.textContent = msg;
      clearTimeout(timer);
      timer = setTimeout(function () {
        btn.textContent = 'Copy URL';
        btn.disabled = false;
      }, 1500);
    }

    btn.addEventListener('click', function () {
      btn.disabled = true;
      copy(fetchUrl(match[1]))
        .then(function () { flash('Copied!'); })
        .catch(function (e) { flash(e.message || 'Could not copy'); });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();