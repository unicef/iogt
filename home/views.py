from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import ManifestSettings


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
        "icons": [
            {
                "src": "",
                "type": f"",
                "sizes": f"{manifest.icon_96_96.height}x{manifest.icon_96_96.width}"
            },
            {
                "src": "",
                "type": f"",
                "sizes": f"{manifest.icon_512_512.height}x{manifest.icon_512_512.width}"
            },
            {
                "src": "",
                "type": f"",
                "sizes": f"{manifest.icon_196_196.height}x{manifest.icon_196_196.width}",
                "purpose": "any maskable"
            }
        ]
    }

    return JsonResponse(response)
