import wagtail_factories
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import PageViewRestriction

from home.factories import (ArticleFactory, BannerIndexPageFactory,
                            BannerPageFactory, FeaturedContentFactory,
                            HomePageBannerFactory, SectionFactory)
from home.models import HomePage
from iogt_users.factories import GroupFactory, UserFactory


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


class HomePageViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(user=self.user)

        self.home_page = HomePage.objects.first()

    def test_home_page(self):
        response = self.client.get('')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'home/section.html')

    def test_home_page_featured_content(self):
        section = SectionFactory.build(owner=self.user)
        article = ArticleFactory.build(owner=self.user)
        self.home_page.add_child(instance=section)
        self.home_page.add_child(instance=article)
        FeaturedContentFactory(source=self.home_page, content=section)
        FeaturedContentFactory(source=self.home_page, content=article)

        response = self.client.get('')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'home/section.html')
        self.assertEqual(len(response.context['featured_content']), 2)

    def test_home_page_return_live_featured_content_only(self):
        section = SectionFactory.build(owner=self.user, live=False)
        article = ArticleFactory.build(owner=self.user, live=False)
        self.home_page.add_child(instance=section)
        self.home_page.add_child(instance=article)
        FeaturedContentFactory(source=self.home_page, content=section)
        FeaturedContentFactory(source=self.home_page, content=article)

        response = self.client.get('')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'home/section.html')
        self.assertEqual(len(response.context['featured_content']), 0)

    def test_home_page_banners(self):
        section = SectionFactory.build(owner=self.user)
        self.home_page.add_child(instance=section)
        banner_index_page = BannerIndexPageFactory.build()
        self.home_page.add_child(instance=banner_index_page)
        banner_page01 = BannerPageFactory.build(banner_image=wagtail_factories.ImageFactory(), banner_link_page=section)
        banner_page02 = BannerPageFactory.build(banner_image=wagtail_factories.ImageFactory(), external_link='https://www.google.com/')
        banner_index_page.add_child(instance=banner_page01)
        banner_index_page.add_child(instance=banner_page02)
        HomePageBannerFactory(source=self.home_page, banner_page=banner_page01)
        HomePageBannerFactory(source=self.home_page, banner_page=banner_page02)

        response = self.client.get('')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'home/section.html')
        self.assertEqual(len(response.context['banners']), 2)

    def test_home_page_return_live_banners_only(self):
        section = SectionFactory.build(owner=self.user)
        self.home_page.add_child(instance=section)
        banner_index_page = BannerIndexPageFactory.build()
        self.home_page.add_child(instance=banner_index_page)
        banner_page01 = BannerPageFactory.build(banner_image=wagtail_factories.ImageFactory(), banner_link_page=section, live=False)
        banner_page02 = BannerPageFactory.build(banner_image=wagtail_factories.ImageFactory(), external_link='https://www.google.com/', live=False)
        banner_index_page.add_child(instance=banner_page01)
        banner_index_page.add_child(instance=banner_page02)
        HomePageBannerFactory(source=self.home_page, banner_page=banner_page01)
        HomePageBannerFactory(source=self.home_page, banner_page=banner_page02)

        response = self.client.get('')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'home/section.html')
        self.assertEqual(len(response.context['banners']), 0)
