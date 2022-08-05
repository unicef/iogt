import unittest

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site

from home.factories import (
    SectionFactory,
    ArticleFactory,
    HomePageFactory,
    SVGToPNGMapFactory,
    LocaleFactory,
    OfflineContentIndexPageFactory,
    MiscellaneousIndexPageFactory
)
from wagtail_factories import ImageFactory, SiteFactory

from iogt.utils import has_md5_hash


class PageTreeAPIViewTests(TestCase):
    def setUp(self):
        self.url_name = 'page_tree'
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.en_locale = LocaleFactory(language_code='en')
        self.ar_locale = LocaleFactory(language_code='ar')
        self.en_home_page = HomePageFactory(parent=self.site.root_page, locale=self.en_locale)
        self.ar_home_page = HomePageFactory(parent=self.site.root_page, locale=self.ar_locale)
        self.en_miscellaneous_index_page = MiscellaneousIndexPageFactory(parent=self.en_home_page)
        self.ar_miscellaneous_index_page = MiscellaneousIndexPageFactory(parent=self.ar_home_page)
        self.en_offline_content_index_page = OfflineContentIndexPageFactory(parent=self.en_miscellaneous_index_page)
        self.ar_offline_content_index_page = OfflineContentIndexPageFactory(parent=self.ar_miscellaneous_index_page)
        self.section = SectionFactory(parent=self.en_home_page)
        self.article = ArticleFactory(parent=self.en_home_page, body=[("image", ImageFactory())])
        self.section_lead_image_rendition = self.section.lead_image.get_rendition('fill-360x360')
        self.article_lead_image_rendition = self.article.lead_image.get_rendition('fill-360x360')
        self.article_body_image_rendition = self.article.body.stream_data[0][1].get_rendition('fill-360x360')
        self.svg_to_png_map = SVGToPNGMapFactory()

    def test_root_page_is_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.en_home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.en_home_page.url, response.data)

    def test_descendants_are_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.en_home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.section.url, response.data)
        self.assertIn(self.article.url, response.data)

    def test_images_are_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.en_home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.section_lead_image_rendition.url, response.data)
        self.assertIn(self.article_lead_image_rendition.url, response.data)
        self.assertIn(self.article_body_image_rendition.url, response.data)
        self.assertIn(self.svg_to_png_map.url, response.data)

    def test_static_assets_are_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.en_home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue([item for item in response.data if item.startswith('/static/css/iogt')])
        self.assertTrue([item for item in response.data if item.startswith('/static/js/iogt')])
        self.assertTrue([item for item in response.data if item.startswith('/static/icons/search')])
        self.assertTrue([item for item in response.data if item.startswith('/static/fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4gaVQUwaEQbjA')])
        self.assertIn('/en/jsi18n/', response.data)
        self.assertIn('/ar/jsi18n/', response.data)

    def test_offline_content_not_found_pages_are_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.en_home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('/en/offline-content-not-found/', response.data)
        self.assertIn('/ar/offline-content-not-found/', response.data)

    def test_offline_content_index_pages_are_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.en_home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.en_offline_content_index_page.url, response.data)
        self.assertIn(self.ar_offline_content_index_page.url, response.data)


class TestUtils(unittest.TestCase):
    def test_has_md5_hash_with_hash_values(self):
        with_md5_hash = [
            'iogt.c288d51a7c1f.css',
            'iogt.9bbc5bdef847.js',
            'search.6f2883e8e48b.svg',
            'memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4gaVQUwaEQbjA.186a2a0afcb7.woff',
        ]

        for value in with_md5_hash:
            self.assertTrue(has_md5_hash(value))

    def test_has_md5_hash_without_has_values(self):
        without_md5_hash = [
            'iogt.css',
            'iogt.js',
            'search.svg',
            'memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4gaVQUwaEQbjA.woff',
        ]

        for value in without_md5_hash:
            self.assertFalse(has_md5_hash(value))
