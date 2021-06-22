from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import PageViewRestriction

from home.factories import ArticleFactory
from home.models import HomePage
from iogt_users.factories import UserFactory, GroupFactory


class PageViewGroupPermissionTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = UserFactory()
        self.admin_user = UserFactory()

        self.home_page = HomePage.objects.first()
        self.group_restricted_article = ArticleFactory.build(owner=self.admin_user)
        self.home_page.add_child(instance=self.group_restricted_article)
        view_restriction = PageViewRestriction.objects.create(page=self.group_restricted_article,
                                                              restriction_type=PageViewRestriction.GROUPS)

        self.allowed_group = GroupFactory(name='Allowed group')
        view_restriction.groups.add(self.allowed_group)

    def test_group_limited_article_without_login_redirects_to_login_page(self):
        response = self.client.get(self.group_restricted_article.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(f'{reverse("account_login")}?next={self.group_restricted_article.url}', response.url)

    def test_group_limited_article_without_group_returns_403(self):
        self.client.login(username=self.user.username, password='test@123')
        response = self.client.get(self.group_restricted_article.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_limited_article_with_group_user_returns_200(self):
        self.user.groups.add(self.allowed_group)
        self.client.login(username=self.user.username, password='test@123')
        response = self.client.get(self.group_restricted_article.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
