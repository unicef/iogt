from django.conf import settings
from django.db.utils import IntegrityError
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import PageViewRestriction
from unittest.mock import patch

from comments.models import CommentStatus
from home.factories import ArticleFactory
from home.models import HomePage, SVGToPNGMap
from iogt_users.factories import UserFactory, GroupFactory


class PageViewGroupPermissionTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = UserFactory()
        self.admin_user = UserFactory()

        self.home_page = HomePage.objects.first()
        self.group_restricted_article = ArticleFactory.build(owner=self.admin_user,
                                                             commenting_status=CommentStatus.OPEN)
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

class SVGToPNGMapTests(TestCase):

    def setUp(self) -> None:
        self.svg_path = 'static/icons/search.svg'

    def test_create_png_if_not_found(self):
        png = SVGToPNGMap.get_png_image(self.svg_path)
        expected_path_regex = ''.join([
            settings.MEDIA_ROOT,
            r"/svg-to-png-maps/svg-to-png_.*\.png"
        ])
        self.assertRegex(png.path, expected_path_regex)
        self.assertGreater(png.size, 0)

        png_2 = SVGToPNGMap.get_png_image(self.svg_path)
        self.assertEquals(png, png_2)

    @patch.object(SVGToPNGMap, 'create')
    def test_get_png_must_not_fail(self, create):
            create.side_effect = Exception('boom')
            png = SVGToPNGMap.get_png_image(self.svg_path)
            self.assertIsNone(png)

    def test_uniqueness_no_stroke_no_fill(self):
        SVGToPNGMap.create(self.svg_path)
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path)

    def test_uniqueness_fill_no_stroke(self):
        SVGToPNGMap.create(self.svg_path, fill_color='#a1b2c3')
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path, fill_color='#a1b2c3')

    def test_uniqueness_stroke_no_fill(self):
        SVGToPNGMap.create(self.svg_path, stroke_color='#fff')
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path, stroke_color='#fff')

    def test_uniqueness_stroke_and_fill(self):
        SVGToPNGMap.create(
            self.svg_path,
            fill_color='#555',
            stroke_color='#666'
        )
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(
                self.svg_path,
                fill_color='#555',
                stroke_color='#666'
            )
