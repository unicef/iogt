from django.test import TestCase, Client

from home.tests import factories


class TransitionArticleForExternalLinksTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.article = factories.ArticleFactory()

    def test_rich_text_field_internal_link_parse_success(self):
        pass

    def test_rich_text_external_link_parse_success(self):
        pass
