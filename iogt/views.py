from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView


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

        sitemap = {
            'home_page': [f'{protocol}://{site}{p.url_path}' for p in HomePage.objects.live()],
            'sections': [f'{protocol}://{site}{p.url_path}' for p in Section.objects.live()],
            'articles': [f'{protocol}://{site}{p.url_path}' for p in Article.objects.live()],
            'footers': [f'{protocol}://{site}{p.url_path}' for p in FooterPage.objects.live()],
        }

        return Response(sitemap)
