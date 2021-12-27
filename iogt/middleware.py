from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.middleware.locale import LocaleMiddleware as DjangoLocaleMiddleware
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import get_language_from_path, check_for_language, get_supported_language_variant
from django.utils.translation.trans_real import get_languages, parse_accept_lang_header, language_code_re
from wagtail.core.models import Locale

from home.models import SiteSettings


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
                return get_supported_language_variant(accept_lang)
            except LookupError:
                continue

        locale = Locale.objects.filter(locale_detail__is_active=True, locale_detail__is_main_language=True).first()
        if locale:
            return locale.language_code
        else:
            return settings.LANGUAGE_CODE

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
