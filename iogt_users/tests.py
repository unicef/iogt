from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from home.factories import ArticleFactory
from home.models import HomePage
from iogt_users.factories import UserFactory


class PostRegistrationRedirectTests(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.admin_user = UserFactory()

        self.home_page = HomePage.objects.first()
        self.public_article = ArticleFactory.build(owner=self.admin_user)
        self.home_page.add_child(instance=self.public_article)

    def test_user_locked_out_without_filling_registration_survey_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, reverse('post_registration_survey'))

    def test_anonymous_user_can_browse_public_urls(self):
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
