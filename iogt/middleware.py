from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.http import HttpResponseRedirect
from django.urls import get_script_prefix, is_valid_path
from django.utils import translation
from django.utils.cache import patch_vary_headers
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


class LocaleMiddleware(MiddlewareMixin):
    """
    Parse a request and decide what translation object to install in the
    current thread context. This allows pages to be dynamically translated to
    the language the user desires (if the language is available).
    """
    response_redirect_class = HttpResponseRedirect

    def _get_language_from_request(self, request, check_path=False):
        """
        Analyze the request to find what language the user wants the system to
        show. Only languages listed in settings.LANGUAGES are taken into account.
        If the user requests a sublanguage where we have a main language, we send
        out the main language.

        If check_path is True, the URL path prefix will be checked for a language
        code, otherwise this is skipped for backwards compatibility.
        """
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

        locale = Locale.objects.filter(locale_detail__is_main_language=True).first()
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

    def process_response(self, request, response):
        language = translation.get_language()
        language_from_path = translation.get_language_from_path(request.path_info)
        urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language = is_language_prefix_patterns_used(urlconf)

        if (response.status_code == 404 and not language_from_path and
                i18n_patterns_used and prefixed_default_language):
            # Maybe the language code is missing in the URL? Try adding the
            # language prefix and redirecting to that URL.
            language_path = '/%s%s' % (language, request.path_info)
            path_valid = is_valid_path(language_path, urlconf)
            path_needs_slash = (
                not path_valid and (
                    settings.APPEND_SLASH and not language_path.endswith('/') and
                    is_valid_path('%s/' % language_path, urlconf)
                )
            )

            if path_valid or path_needs_slash:
                script_prefix = get_script_prefix()
                # Insert language after the script prefix and before the
                # rest of the URL
                language_url = request.get_full_path(force_append_slash=path_needs_slash).replace(
                    script_prefix,
                    '%s%s/' % (script_prefix, language),
                    1
                )
                return self.response_redirect_class(language_url)

        if not (i18n_patterns_used and language_from_path):
            patch_vary_headers(response, ('Accept-Language',))
        response.setdefault('Content-Language', language)
        return response


class AdminLocaleMiddleware(MiddlewareMixin):
    """Ensures that the admin locale doesn't change with user selection"""

    def process_request(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/django-admin/'):
            translation.activate(settings.LANGUAGE_CODE)
