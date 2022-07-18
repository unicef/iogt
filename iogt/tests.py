from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from wagtail.core.models import Site

from home.factories import SectionFactory, ArticleFactory, HomePageFactory, SVGToPNGMapFactory
from wagtail_factories import ImageFactory, SiteFactory


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
        self.assertIn('/static/css/iogt.css', response.data)
        self.assertIn('/static/js/iogt.js', response.data)
        self.assertIn('/static/icons/search.svg', response.data)
        self.assertIn('/static/fonts/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsg-1x4gaVQUwaEQbjA.woff', response.data)
