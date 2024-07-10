from unittest.mock import patch

from django.conf import settings
from django.db.utils import IntegrityError
from django.test import TestCase
from django.urls import reverse
from iogt_users.factories import GroupFactory, UserFactory
from rest_framework import status
from wagtail.models import PageViewRestriction, Site
from wagtail_factories import SiteFactory

from home.factories import ArticleFactory, HomePageFactory
from home.models import SVGToPNGMap


class PageViewGroupPermissionTests(TestCase):
    def setUp(self):
        self.user = UserFactory()

        Site.objects.all().delete()
        self.site = SiteFactory(site_name="IoGT", port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

        self.group_restricted_article = ArticleFactory(parent=self.home_page)
        view_restriction = PageViewRestriction.objects.create(
            page=self.group_restricted_article,
            restriction_type=PageViewRestriction.GROUPS,
        )

        self.allowed_group = GroupFactory(name="Allowed group")
        view_restriction.groups.add(self.allowed_group)

    def test_group_limited_article_without_login_redirects_to_login_page(self):
        response = self.client.get(self.group_restricted_article.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(
            f'{reverse("account_login")}?next={self.group_restricted_article.url}',
            response.url,
        )

    def test_group_limited_article_without_group_returns_403(self):
        self.client.login(username=self.user.username, password="test@123")
        response = self.client.get(self.group_restricted_article.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_limited_article_with_group_user_returns_200(self):
        self.user.groups.add(self.allowed_group)
        self.client.login(username=self.user.username, password="test@123")
        response = self.client.get(self.group_restricted_article.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SVGToPNGMapTests(TestCase):

    def setUp(self) -> None:
        self.svg_path = "static/icons/search.svg"

    def test_create_png_if_not_found(self):
        png = SVGToPNGMap.get_png_image(self.svg_path)
        expected_path_regex = "".join(
            [settings.MEDIA_ROOT, r"/svg-to-png-maps/svg-to-png.*\.png"]
        )
        self.assertRegex(png.path, expected_path_regex)
        self.assertGreater(png.size, 0)

        png_2 = SVGToPNGMap.get_png_image(self.svg_path)
        self.assertEquals(png, png_2)

    def test_ignore_duplicates(self):
        png = SVGToPNGMap.get_png_image(self.svg_path)
        duplicate = {
            "svg_path": self.svg_path,
            "fill_color": None,
            "stroke_color": None,
            "png_image_file": png,
        }
        SVGToPNGMap.objects.create(**duplicate)
        SVGToPNGMap.objects.create(**duplicate)
        count = SVGToPNGMap.objects.filter(
            svg_path=self.svg_path, fill_color=None, stroke_color=None
        ).count()
        self.assertEquals(count, 2)
        png_2 = SVGToPNGMap.get_png_image(self.svg_path, None, None)
        self.assertEquals(png, png_2)

    @patch.object(SVGToPNGMap, "create")
    def test_get_png_must_not_fail(self, create):
        create.side_effect = Exception("boom")
        png = SVGToPNGMap.get_png_image(self.svg_path)
        self.assertIsNone(png)

    def test_uniqueness_unspecified_stroke_and_fill(self):
        SVGToPNGMap.create(self.svg_path)
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path)

    def test_uniqueness_no_stroke_and_fill(self):
        SVGToPNGMap.create(self.svg_path, None, None)
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path, None, None)

    def test_uniqueness_fill_no_stroke(self):
        SVGToPNGMap.create(self.svg_path, fill_color="#a1b2c3", stroke_color=None)
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path, fill_color="#a1b2c3", stroke_color=None)

    def test_uniqueness_stroke_no_fill(self):
        SVGToPNGMap.create(self.svg_path, fill_color=None, stroke_color="#fff")
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path, fill_color=None, stroke_color="#fff")

    def test_uniqueness_stroke_and_fill(self):
        SVGToPNGMap.create(self.svg_path, fill_color="#555", stroke_color="#666")
        with self.assertRaises(IntegrityError):
            SVGToPNGMap.create(self.svg_path, fill_color="#555", stroke_color="#666")
