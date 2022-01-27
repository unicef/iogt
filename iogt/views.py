from django.contrib.admin.utils import flatten
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView
from wagtail.core.models import Page

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
        from home.models import HomePage, Section, Article

        home_page_urls = [p.full_url for p in HomePage.objects.live()],
        section_urls = [p.full_url for p in Section.objects.live()],
        article_urls = [p.full_url for p in Article.objects.live()],
        poll_urls = [p.full_url for p in Poll.objects.live()],
        survey_urls = [p.full_url for p in Survey.objects.live()],
        quiz_urls = [p.full_url for p in Quiz.objects.live()],

        sitemap = flatten(home_page_urls + section_urls + article_urls + poll_urls + survey_urls + quiz_urls)

        return Response(sitemap)
