import logging
import os
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.contrib.admin.utils import flatten
from django.shortcuts import get_object_or_404, redirect
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from django.contrib.auth import logout
from django.views import View
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.models import Page, Locale
from wagtail.images.models import Rendition
from wagtailmedia.models import Media

from home.models import HomePage, Section, Article, SVGToPNGMap, FooterPage, OfflineContentIndexPage
from iogt.utils import has_md5_hash
from questionnaires.models import Poll, Survey, Quiz

from admin_login.azure_utility import get_azure_auth_details

logger = logging.getLogger(__name__)


class TransitionPageView(TemplateView):
    template_name = "transition-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["next"] = self.request.GET.get("next", "/")
        context["prev"] = self.request.META.get("HTTP_REFERER", "/")
        return context


class TranslationNotFoundPage(TemplateView):
    template_name = "translation_not_found_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        from home.models import HomePage
        origin_page = get_object_or_404(Page, pk=self.request.GET.get('page'))

        context['home_page'] = HomePage.objects.first().localized
        context['prev'] = origin_page.url

        context['page_title'] = origin_page.title
        return context


class SitemapAPIView(APIView):
    def get(self, request):
        home_page_urls = [p.url for p in HomePage.objects.live()]
        section_urls = [p.url for p in Section.objects.live()]
        article_urls = [p.url for p in Article.objects.live()]
        footer_urls = [p.url for p in FooterPage.objects.live()]
        poll_urls = [p.url for p in Poll.objects.live()]
        survey_urls = [p.url for p in Survey.objects.live()]
        quiz_urls = [p.url for p in Quiz.objects.live()]

        jsi18n_urls = []
        for locale in Locale.objects.all():
            jsi18n_urls.append(f'/{locale.language_code}/jsi18n/')

        image_urls = []
        for image in Rendition.objects.all():
            image_urls.append(f'{settings.MEDIA_URL}{image.file.name}')

        for image in SVGToPNGMap.objects.all():
            image_urls.append(f'{settings.MEDIA_URL}{image.png_image_file.name}')

        media_urls = []
        for media in Media.objects.all():
            media_urls.append(f'{settings.MEDIA_URL}{media.file.name}')
            if media.thumbnail:
                image_urls.append(f'{settings.MEDIA_URL}{media.thumbnail.name}')

        static_urls = []
        static_dirs = [
            {'name': 'css', 'extensions': ('.css',)},
            {'name': 'js', 'extensions': ('.js',)},
            {'name': 'fonts', 'extensions': ('.woff', '.woff2',)},
            {'name': 'icons', 'extensions': ('.svg',)},
        ]
        for static_dir in static_dirs:
            for root, dirs, files in os.walk(Path(settings.STATIC_ROOT) / static_dir['name']):
                for file in files:
                    if file.endswith(static_dir['extensions']):
                        static_urls.append(f'{settings.STATIC_URL}{root.split("/static/")[-1]}/{file}')

        sitemap = set(flatten(
            home_page_urls +
            section_urls +
            article_urls +
            footer_urls +
            poll_urls +
            survey_urls +
            quiz_urls +
            static_urls +
            image_urls +
            media_urls +
            jsi18n_urls
        ))
        return Response(sitemap)


class PageTreeAPIView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, page_id):
        page = get_object_or_404(Page, id=page_id)
        pages = page.get_descendants(inclusive=True).live().specific()
        page_urls = []
        active_locale = Locale.get_active()
        for locale in Locale.objects.all():
            translation.activate(locale.language_code)
            page_urls.append(reverse('offline_content_not_found'))
            page_urls.append(reverse('javascript-catalog'))
            page = OfflineContentIndexPage.objects.filter(locale=locale).first()
            if page:
                page_urls.append(page.url)
        translation.activate(active_locale.language_code)

        no_impl = set()
        for page in pages:
            try:
                page_urls += page.offline_urls
            except AttributeError:
                no_impl.add(type(page).__name__)

        if no_impl:
            types = ", ".join(sorted(no_impl))
            logger.warn(
                f"Offline URLs could not be obtained for the following Page types: "
                f"{types}"
            )

        image_urls = []
        for svg_to_png_map in SVGToPNGMap.objects.all():
            image_urls.append(svg_to_png_map.url)

        static_urls = []
        static_dirs = [
            {'name': 'css', 'extensions': ('.css',)},
            {'name': 'js', 'extensions': ('.js',)},
            {'name': 'fonts', 'extensions': ('.woff', '.woff2',)},
            {'name': 'icons', 'extensions': ('.svg',)},
        ]
        for static_dir in static_dirs:
            for root, dirs, files in os.walk(Path(settings.STATIC_ROOT).joinpath(static_dir['name'])):
                for file in files:
                    if file.endswith(static_dir['extensions']):
                        try:
                            if not has_md5_hash(file):
                                static_urls.append(
                                    static(f'{PurePosixPath(root).relative_to(settings.STATIC_ROOT).joinpath(file)}'))
                        except Exception as e:
                            logger.exception(e)

        urls = set(flatten(
            page_urls +
            image_urls +
            static_urls
        ))
        return Response(urls)


class OfflineContentNotFoundPageView(TemplateView):
    template_name = "offline_content_not_found.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        page = OfflineContentIndexPage.objects.filter(locale=Locale.get_active()).first()
        context["offline_content_index_page_url"] = (page and page.url) or ''
        return context


class CustomLogoutView(View):
    """
    This view handles user logout from both Django and Azure AD B2C.
    After logging out the user from Django, it also logs out from Azure AD B2C.
    """
    def get(self, request, *args, **kwargs):
        return self.handle_logout(request)
       
    def post(self, request, *args, **kwargs):
        return self.handle_logout(request)
    
    def handle_logout(self, request):
        """
        Log the user out of Django and redirect them to Azure AD B2C's logout page.
        """
        # Log the user out of the Django session
        logout(request)

        # Azure AD B2C logout URL
        azure_logout_url = self.get_azure_ad_b2c_logout_url(request)

        # Redirect to Azure AD B2C logout
        return redirect(azure_logout_url)

    def get_azure_ad_b2c_logout_url(self, request):
        """
        Generate the Azure AD B2C logout URL.
        This URL will redirect the user to the Azure AD B2C logout endpoint.
        """
        # Get the tenant and policy (e.g., B2C_1_signup_signin) from settings or your configuration
        azure_details = get_azure_auth_details()
        tenant = azure_details['tenant_id']
        policy = azure_details['policy']
        redirect_uri = azure_details['redirect_uri']
        # Azure AD B2C logout URL (This URL will log the user out of Azure AD and redirect them back to your app)
        logout_url = f"https://{tenant}.b2clogin.com/{tenant}.onmicrosoft.com/{policy}/oauth2/v2.0/logout?p={policy}&post_logout_redirect_uri={redirect_uri}"

        return logout_url