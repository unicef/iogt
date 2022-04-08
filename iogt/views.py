from django.contrib.admin.utils import flatten
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.core.models import Page
from wagtail.images.models import Image

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
        from home.models import HomePage, Section, Article, FooterPage
        from wagtail.images.views.serve import generate_image_url


        home_page_urls = [p.full_url for p in HomePage.objects.live()],
        section_urls = [p.full_url for p in Section.objects.live()],
        article_urls = [p.full_url for p in Article.objects.live()],
        footer_urls = [p.full_url for p in FooterPage.objects.live()],
        poll_urls = [p.full_url for p in Poll.objects.live()],
        survey_urls = [p.full_url for p in Survey.objects.live()],
        quiz_urls = [p.full_url for p in Quiz.objects.live()],

        image_urls = []
        for image in Image.objects.all():
            image_urls.append(request.build_absolute_uri(generate_image_url(image, 'width-360')))

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
        ]
        static_urls = []
        for static_path in static_paths:
            static_urls.append(request.build_absolute_uri(static(static_path)))

        sitemap = flatten(
            tuple(image_urls) + tuple(static_urls) +
            home_page_urls + section_urls + article_urls + footer_urls + poll_urls + survey_urls + quiz_urls
        )

        return Response(sitemap)
