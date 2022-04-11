from django.conf import settings
from django.contrib.admin.utils import flatten
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.core.models import Page
from wagtail.images.models import Rendition

from questionnaires.models import Poll, Survey, Quiz


def check_user_session(request):
    if request.method == "POST":
        request.session["first_time_user"] = False


def create_final_external_link(next_page):
    transition_page = reverse("external-link")
    return f"{transition_page}?next={next_page}"


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
        from home.models import HomePage, Section, Article, FooterPage, SVGToPNGMap

        home_page_urls = [p.url for p in HomePage.objects.live()],
        section_urls = [p.url for p in Section.objects.live()],
        article_urls = [p.url for p in Article.objects.live()],
        footer_urls = [p.url for p in FooterPage.objects.live()],
        poll_urls = [p.url for p in Poll.objects.live()],
        survey_urls = [p.url for p in Survey.objects.live()],
        quiz_urls = [p.url for p in Quiz.objects.live()],

        image_urls = []
        for image in Rendition.objects.all():
            image_urls.append(f'{settings.MEDIA_URL}{image.file.name}')

        for image in SVGToPNGMap.objects.all():
            image_urls.append(f'{settings.MEDIA_URL}{image.png_image_file.name}')

        static_paths = [
            'css/report-page/report-page.css',
            'css/global/global.css',
            'css/questionnaires.css',
            'css/search.css',
            'css/footer/footer.css',
            'css/header/header.css',
            'css/navbar/navbar.css',
            'css/accounts.css',
            'css/chatbot.css',
            'css/iogt.css',
            'css/user-profile.css',
            'css/blocks/skiplogic.css',
            'css/polls.css',
            'css/polls.css',
            'css/questionnaire.css',
            'css/quiz.css',
            'css/survey.css',
            'js/iogt.js',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4gaVQUwaEQbjA.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4iaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4jaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4kaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4saVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4taVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4uaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4vaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4gaVQUwaEQbjA.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4iaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4jaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4kaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4saVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4taVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4uaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsiH0B4vaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4gaVQUwaEQbjA.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4iaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4jaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4kaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4saVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4taVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4uaVQUwaEQbjB_mQ.woff',
            'fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4vaVQUwaEQbjB_mQ.woff',
            'fonts/pxiByp8kv8JHgFVrLCz7Z1JlFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLCz7Z1xlFd2JQEk.woff2',
            'fonts/pxiByp8kv8JHgFVrLCz7Z11lFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLDD4Z1JlFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLDD4Z1xlFd2JQEk.woff2',
            'fonts/pxiByp8kv8JHgFVrLDD4Z11lFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLDz8Z1JlFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLDz8Z1xlFd2JQEk.woff2',
            'fonts/pxiByp8kv8JHgFVrLEj6Z1JlFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLEj6Z1xlFd2JQEk.woff2',
            'fonts/pxiByp8kv8JHgFVrLEj6Z11lFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLFj_Z1JlFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLFj_Z1xlFd2JQEk.woff2',
            'fonts/pxiByp8kv8JHgFVrLFj_Z11lFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLGT9Z1JlFd2JQEl8qw.woff2',
            'fonts/pxiByp8kv8JHgFVrLGT9Z1xlFd2JQEk.woff2',
            'fonts/pxiByp8kv8JHgFVrLGT9Z11lFd2JQEl8qw.woff2',
            'fonts/pxiEyp8kv8JHgFVrJJbecnFHGPezSQ.woff2',
            'fonts/pxiEyp8kv8JHgFVrJJfecnFHGPc.woff2',
            'fonts/pxiEyp8kv8JHgFVrJJnecnFHGPezSQ.woff2',
            'fonts/pxiGyp8kv8JHgFVrLPTucHtAOvWDSA.woff2',
            'fonts/pxiGyp8kv8JHgFVrLPTucXtAOvWDSHFF.woff2',
            'fonts/pxiGyp8kv8JHgFVrLPTufntAOvWDSHFF.woff2',
        ]
        static_urls = []
        for static_path in static_paths:
            static_urls.append(f'{settings.STATIC_URL}{static_path}')

        sitemap = flatten(
            home_page_urls +
            section_urls +
            article_urls +
            footer_urls +
            poll_urls +
            survey_urls +
            quiz_urls +
            tuple(static_urls) +
            tuple(image_urls)
        )
        return Response(sitemap)
