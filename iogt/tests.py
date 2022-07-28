import unittest

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site

from home.factories import SectionFactory, ArticleFactory, HomePageFactory, SVGToPNGMapFactory
from wagtail_factories import ImageFactory, SiteFactory

from iogt.utils import has_md5_hash


class PageTreeAPIViewTests(TestCase):
    def setUp(self):
        self.url_name = 'page_tree'
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

    def test_root_page_is_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.home_page.url, response.data)

    def test_descendants_are_returned(self):
        section = SectionFactory(parent=self.home_page)
        article = ArticleFactory(parent=self.home_page)

        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(section.url, response.data)
        self.assertIn(article.url, response.data)

    def test_images_are_returned(self):
        section = SectionFactory(parent=self.home_page)
        article = ArticleFactory(parent=self.home_page, body=[("image", ImageFactory())])
        section_lead_image_rendition = section.lead_image.get_rendition('fill-360x360')
        article_lead_image_rendition = article.lead_image.get_rendition('fill-360x360')
        article_body_image_rendition = article.body.stream_data[0][1].get_rendition('fill-360x360')
        svg_to_png_map = SVGToPNGMapFactory()

        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(section_lead_image_rendition.url, response.data)
        self.assertIn(article_lead_image_rendition.url, response.data)
        self.assertIn(article_body_image_rendition.url, response.data)
        self.assertIn(svg_to_png_map.url, response.data)

    def test_static_assets_are_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue([item for item in response.data if item.startswith('/static/css/iogt')])
        self.assertTrue([item for item in response.data if item.startswith('/static/js/iogt')])
        self.assertTrue([item for item in response.data if item.startswith('/static/icons/search')])
        self.assertTrue([item for item in response.data if item.startswith('/static/fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4gaVQUwaEQbjA')])


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
