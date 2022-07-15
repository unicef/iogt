from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from home.factories import SectionFactory, ArticleFactory
from home.models import HomePage
from wagtail_factories import ImageFactory


class PageTreeAPIViewTests(TestCase):
    def setUp(self):
        self.url_name = 'page_tree'
        self.home_page = HomePage.objects.first()

    def test_root_page_is_returned(self):
        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.home_page.url, response.data)

    def test_descendants_are_returned(self):
        section = SectionFactory.build()
        article = ArticleFactory.build()
        self.home_page.add_child(instance=section)
        section.add_child(instance=article)

        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(section.url, response.data)
        self.assertIn(article.url, response.data)

    def test_images_are_returned(self):
        section = SectionFactory.build(lead_image=ImageFactory())
        article = ArticleFactory.build(lead_image=ImageFactory())
        self.home_page.add_child(instance=section)
        section.add_child(instance=article)
        section_lead_image_rendition = section.lead_image.get_rendition('fill-360x360')
        article_lead_image_rendition = article.lead_image.get_rendition('fill-360x360')

        response = self.client.get(reverse(self.url_name, kwargs={'page_id': self.home_page.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(section_lead_image_rendition.url, response.data)
        self.assertIn(article_lead_image_rendition.url, response.data)
