from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from .models import ManifestSettings


class ServiceWorkerView(TemplateView):
    template_name = "sw.js"
    content_type = "application/javascript"
    name = "sw.js"


def get_manifest(request):
    language = request.LANGUAGE_CODE
    manifest = get_object_or_404(ManifestSettings, language=language)
    response = {
        "name": manifest.name,
        "short_name": manifest.short_name,
        "scope": manifest.scope,
        "background_color": manifest.background_color,
        "theme_color": manifest.theme_color,
        "description": manifest.description,
        "lang": manifest.language,
        "start_url": manifest.start_url,
        "display": manifest.display,
        "icons": [
            {
                "src": f"{manifest.icon_96_96.file.url}",
                "type": f"image/{manifest.icon_96_96.title.split('.')[1]}",
                "sizes": f"{manifest.icon_96_96.height}x{manifest.icon_96_96.width}",
            },
            {
                "src": f"{manifest.icon_512_512.file.url}",
                "type": f"image/{manifest.icon_512_512.title.split('.')[1]}",
                "sizes": f"{manifest.icon_512_512.height}x{manifest.icon_512_512.width}",
            },
            {
                "src": f"{manifest.icon_196_196.file.url}",
                "type": f"image/{manifest.icon_196_196.title.split('.')[1]}",
                "sizes": f"{manifest.icon_196_196.height}x{manifest.icon_196_196.width}",
                "purpose": "any maskable",
            },
        ],
    }

    http_response = JsonResponse(response)
    http_response['Content-Disposition'] = 'attachment; filename="manifest.json"'
    return http_response


class LogoutRedirectHackView(View):
    def get(self, request):
        return redirect(f'/{request.LANGUAGE_CODE}/')
