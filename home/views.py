from django.conf import settings
from django.contrib import messages
from django.core.management import call_command
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from translation_manager.manager import Manager
from wagtail.contrib.modeladmin.views import EditView

from iogt.patch import patch_store_to_db
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


class TranslationEditView(EditView):
    def post(self, request, *args, **kwargs):
        super(TranslationEditView, self).post(request, *args, **kwargs)
        patch_store_to_db()

        manager = Manager()
        for language, language_name in settings.LANGUAGES:
            manager.update_po_from_db(lang=language)

        return redirect(request.META['HTTP_REFERER'])


class LoadTranslationsFromPOFiles(View):
    def get(self, request):
        call_command('reload_po_files')

        messages.success(request, _('The translations have been loaded successfully!'))

        return redirect(request.META['HTTP_REFERER'])
