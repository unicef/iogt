from django.contrib.admin.utils import flatten
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

from questionnaires.models import Poll, Survey


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


class SitemapAPIView(APIView):
    def get(self, request):
        from home.models import HomePage, Section, Article, FooterPage

        protocol = request.scheme
        site = get_current_site(request)

        home_page_urls = [f'{protocol}://{site}{p.url}' for p in HomePage.objects.live()],
        section_urls = [f'{protocol}://{site}{p.url}' for p in Section.objects.live()],
        article_urls = [f'{protocol}://{site}{p.url}' for p in Article.objects.live()],
        footer_urls = [f'{protocol}://{site}{p.url}' for p in FooterPage.objects.live()],
        poll_urls = [f'{protocol}://{site}{p.url}' for p in Poll.objects.live()],
        survey_urls = [f'{protocol}://{site}{p.url}' for p in Survey.objects.live()],

        sitemap = flatten(home_page_urls + section_urls + article_urls + footer_urls + poll_urls + survey_urls)

        return Response(sitemap)
