from bs4 import BeautifulSoup
from django.test import TestCase, Client
from rest_framework import status
from wagtail.core.models import Page
from wagtail.core.rich_text import RichText

from home.models import Article
from home.tests.faker import faker


class TransitionArticleForExternalLinksTests(TestCase):
    external_link_pattern = "/external-link/?next="

    def setUp(self) -> None:
        self.client = Client()

    def create_published_article_to_root(self, body) -> Article:
        parent: Page = Page.objects.get(url_path='/home/')  # should be const
        article: Article = Article(title=faker.pystr(), slug=faker.pystr(), body=body)
        parent.add_child(instance=article)
        article.save_revision().publish()

        return article

    def test_if_rich_text_field_internal_links_redirect_directly(self):
        body = [
            ("paragraph", RichText('<p><a href="http://aynthing.com">external link on beginning</a> dolor sit amet</p>')),
            ("paragraph", RichText('<p>Lorem ipsum <a href="http://aynthing.com">external link in middle</a> dolor sit amet</p>')),
            ("paragraph", RichText('<p>Lorem dolor sit amet <a href="http://aynthing.com">external link at the end</a></p>')),
        ]

        article = self.create_published_article_to_root(body=body)
        response = self.client.get(article.get_url())

        assert response.status_code == status.HTTP_200_OK

        html_parser = BeautifulSoup(response.content, "html.parser")
        main_block = html_parser.find("div", {"class": "main-text"})

        assert len(main_block.find_all("a")) == len(body)

        for link in main_block.find_all("a"):
            assert self.external_link_pattern in link["href"]


    def test_rich_text_external_link_parse_success(self):
        pass
