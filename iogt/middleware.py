from urllib.parse import unquote

from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.core.cache import cache
from django.http.response import HttpResponsePermanentRedirect, HttpResponseNotFound
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import get_language_from_path, check_for_language, get_supported_language_variant
from django.utils.translation.trans_real import get_languages, parse_accept_lang_header, language_code_re
from translation_manager.models import TranslationEntry
from wagtail.contrib.redirects.middleware import RedirectMiddleware
from wagtail.core.models import Locale, Site

from home.models import SiteSettings, V1PageURLToV2PageMap, ThemeSettings, SVGToPNGMap
import iogt.iogt_globals as globals_


class CacheControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if SiteSettings.for_request(request).opt_in_to_google_web_light:
            response['Cache-Control'] = 'no-transform'

        return response


class LocaleMiddleware(DjangoLocaleMiddleware):
    def _get_language_from_request(self, request, check_path=False):
        if check_path:
            lang_code = get_language_from_path(request.path_info)
            if lang_code is not None:
                return lang_code

        lang_code = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        if lang_code is not None and lang_code in get_languages() and check_for_language(lang_code):
            return lang_code

        try:
            return get_supported_language_variant(lang_code)
        except LookupError:
            pass

        accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        for accept_lang, unused in parse_accept_lang_header(accept):
            if accept_lang == '*':
                break

            if not language_code_re.search(accept_lang):
                continue

            try:
                lang_code = get_supported_language_variant(accept_lang)
            except LookupError:
                continue

            if Locale.objects.filter(language_code=lang_code, locale_detail__is_active=True).exists():
                return lang_code

        locale = Locale.objects.filter(locale_detail__is_active=True, locale_detail__is_main_language=True).first()
        return locale.language_code if locale else settings.LANGUAGE_CODE

    def process_request(self, request):
        urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        i18n_patterns_used, __ = is_language_prefix_patterns_used(urlconf)
        language = self._get_language_from_request(request, check_path=i18n_patterns_used)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()


class AdminLocaleMiddleware(MiddlewareMixin):
    """Ensures that the admin locale doesn't change with user selection"""

    def process_request(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/django-admin/'):
            translation.activate(settings.LANGUAGE_CODE)


class CustomRedirectMiddleware(RedirectMiddleware):
    def process_response(self, request, response):
        """
        This custom middleware is written to mitigate broken links from IOGT v1.
        See https://github.com/unicef/iogt/issues/850 for more details.
        """

        return_value = super().process_response(request, response)

        # If the page is not found by wagtail RedirectMiddleware, look for the page in V1PageURLToV2PageMap.
        # If you find the page, redirect the user to the new page.
        if return_value.status_code == 404:
            url = unquote(request.get_full_path())
            if url.startswith('/en/api/'):
                return HttpResponseNotFound(
                    f"Sorry, the requested resource was not found. Please refer to the <a href='/api/docs/'>API documentation</a>."
                )

            page = V1PageURLToV2PageMap.get_page_or_none(url)
            if page:
                return HttpResponsePermanentRedirect(page.url)

        return return_value


class GlobalDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        site = Site.objects.filter(is_default_site=True).first()
        locale = Locale.get_active()
        language_code = locale.language_code
        globals_.site = site
        globals_.site_settings = SiteSettings.for_request(request)
        globals_.theme_settings = ThemeSettings.for_site(site)
        globals_.locale = locale
        if not cache.get('svg_to_png_map'):
            map = {}
            for svg_to_png_map in SVGToPNGMap.objects.all():
                map.update({
                    (svg_to_png_map.svg_path, svg_to_png_map.fill_color, svg_to_png_map.stroke_color): svg_to_png_map,
                })
            cache.set('svg_to_png_map', map)
        if not cache.get(f'{language_code}_translation_map'):
            map = {}
            for translation_entry in TranslationEntry.objects.filter(language=language_code):
                map.update({
                    (translation_entry.original, language_code): translation_entry
                })
            cache.set(f'{language_code}_translation_map', map)

        response = self.get_response(request)

        return response
