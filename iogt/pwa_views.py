# iogt/iogt/pwa_views.py
import json
from django.conf import settings
from django.http import HttpResponse
from django.templatetags.static import static
from django.contrib.staticfiles import finders

def _read_static(path):
    fp = finders.find(path)
    if not fp:
        return None
    with open(fp, "rb") as f:
        return f.read()

def manifest(request):
    # Keep icons under static/pwa/icons/
    data = {
        "name": getattr(settings, "PWA_APP_NAME", "IOGT"),
        "short_name": getattr(settings, "PWA_APP_SHORT_NAME", "IOGT"),
        "start_url": "/?utm_source=homescreen",
        "scope": "/",
        "display": "standalone",
        "background_color": getattr(settings, "PWA_BG_COLOR", "#ffffff"),
        "theme_color": getattr(settings, "PWA_THEME_COLOR", "#493174"),
        "icons": [
            {"src": static("pwa/icons/icon-192.png"), "sizes": "192x192", "type": "image/png"},
            {"src": static("pwa/icons/icon-512.png"), "sizes": "512x512", "type": "image/png"},
            {"src": static("pwa/icons/maskable-512.png"), "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    return HttpResponse(json.dumps(data), content_type="application/manifest+json; charset=utf-8")

def service_worker(request):
    """
    Serve a root-scoped SW with correct headers.
    We load the built file from static: pwa/service-worker.js
    """
    content = _read_static("pwa/service-worker.js") or b"// SW missing"
    resp = HttpResponse(content, content_type="application/javascript; charset=utf-8")
    resp["Service-Worker-Allowed"] = "/"
    # Avoid long-cache so updates propagate (Workbox handles asset caching)
    resp["Cache-Control"] = "no-cache"
    return resp
