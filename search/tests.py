from django.core import management
from django.test import TestCase
from django.urls import reverse

from home.factories import ArticleFactory
from home.models import HomePage
from iogt_users.factories import UserFactory


class SearchViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(user=self.user)
        self.url = reverse('search')
        self.home_page = HomePage.objects.first()

    def test_search_without_query(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')
        self.assertEqual(len(response.context['search_results'].object_list), 0)

    def test_search_with_query(self):
        article01 = ArticleFactory.build(owner=self.user)
        article02 = ArticleFactory.build(owner=self.user)
        article03 = ArticleFactory.build(title='youth', owner=self.user)
        self.home_page.add_child(instance=article01)
        self.home_page.add_child(instance=article02)
        self.home_page.add_child(instance=article03)

        management.call_command('update_index')

        response = self.client.get(f'{self.url}?query=article')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')
        self.assertEqual(len(response.context['search_results'].object_list), 2)

    def test_search_return_live_articles_only(self):
        article01 = ArticleFactory.build(owner=self.user)
        article02 = ArticleFactory.build(owner=self.user)
        article03 = ArticleFactory.build(live=False, owner=self.user)
        self.home_page.add_child(instance=article01)
        self.home_page.add_child(instance=article02)
        self.home_page.add_child(instance=article03)

        management.call_command('update_index')

        response = self.client.get(f'{self.url}?query=article')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')
        self.assertEqual(len(response.context['search_results'].object_list), 2)

    def test_search_with_paginator(self):
        for i in range(20):
            article = ArticleFactory.build(owner=self.user)
            self.home_page.add_child(instance=article)

        management.call_command('update_index')

        response = self.client.get(f'{self.url}?query=article&page=2')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search/search.html')
        self.assertEqual(len(response.context['search_results'].object_list), 9)
        self.assertTrue(response.context['search_results'].has_previous())
        self.assertTrue(response.context['search_results'].has_next())
        self.assertEqual(response.context['search_results'].previous_page_number(), 1)
        self.assertEqual(response.context['search_results'].next_page_number(), 3)
