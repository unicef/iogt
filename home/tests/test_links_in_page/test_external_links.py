from bs4 import BeautifulSoup
from django.test import TestCase

from rest_framework import status
from wagtail.core.models import Site
from wagtail.core.rich_text import RichText

from home.factories import ArticleFactory, HomePageFactory
from wagtail_factories import SiteFactory


class TransitionPageForExtIntLinksInRichTextTests(TestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)
        self.external_link_pattern = "/external-link/?next="

    def test_if_rich_text_field_external_links_redirect_to_transition_page(self):
        body = [
            (
                "paragraph",
                RichText(
                    '<p><a href="https://aynthing.com">external link at the beginning</a> dolor sit amet</p>'
                ),
            ),
            (
                "paragraph",
                RichText(
                    '<p>Lorem ipsum <a href="https://aynthing.com">external link in middle</a> dolor sit amet</p>'
                ),
            ),
            (
                "paragraph",
                RichText(
                    '<p>Lorem dolor sit amet <a href="https://aynthing.com">external link at the end</a></p>'
                ),
            ),
        ]

        article = ArticleFactory(parent=self.home_page, body=body)
        response = self.client.get(article.get_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        html_parser = BeautifulSoup(response.content, "html.parser")
        links = html_parser.select("section.article__content .block-paragraph a")

        self.assertEqual(len(links), len(body))

        for link in links:
            self.assertIn(self.external_link_pattern, link["href"])

    def test_if_rich_text_field_internal_links_redirect_directly(self):
        body = [
            (
                "paragraph",
                RichText(
                    f'<p><a id="{self.home_page.id}" linktype="page">internal link at the beginning</a> dolor sit amet</p>'
                ),
            ),
            (
                "paragraph",
                RichText(
                    f'<p>Lorem ipsum <a id="{self.home_page.id}" linktype="page">internal link in middle</a> dolor sit amet</p>'
                ),
            ),
            (
                "paragraph",
                RichText(
                    f'<p>Lorem dolor sit amet <a id="{self.home_page.id}" linktype="page">internal link at the end</a></p>'
                ),
            ),
        ]

        article = ArticleFactory(parent=self.home_page, body=body)
        response = self.client.get(article.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        html_parser = BeautifulSoup(response.content, "html.parser")
        links = html_parser.select("section.article__content .block-paragraph a")

        self.assertEqual(len(links), len(body))

        for link in links:
            self.assertNotIn(self.external_link_pattern, link["href"])
