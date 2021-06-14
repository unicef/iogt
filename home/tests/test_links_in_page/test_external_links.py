from django.test import TestCase, Client
from wagtail.core.models import Page

from home.models import Article
from home.tests.faker import faker


class TransitionArticleForExternalLinksTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def create_published_article_to_root(self, body) -> Article:
        parent: Page = Page.objects.get(url_path='/home/')  # should be const
        article: Article = Article(title=faker.pystr(), slug=faker.pystr(), body=body)
        parent.add_child(instance=article)
        article.save_revision().publish()

        return article

    def test_if_rich_text_field_internal_links_redirect_directly(self):
        article = self.create_published_article_to_root(body="some BODY")
        response = self.client.get(article.get_url())

    def test_rich_text_external_link_parse_success(self):
        pass
