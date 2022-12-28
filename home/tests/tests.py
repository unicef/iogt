from bs4 import BeautifulSoup
from django.test import TestCase
from django.http import HttpRequest
from wagtail.core.models import Site

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, ArticleFactory, HomePageFactory, SectionIndexFactory
from wagtail_factories import SiteFactory

from questionnaires.factories import PollFactory, SurveyFactory, QuizFactory


class LimitPageChooserHookTests(TestCase):
    def setUp(self):
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

        self.article01 = ArticleFactory(parent=self.home_page)
        self.section01 = SectionFactory(parent=self.home_page)
        self.section02 = SectionFactory(parent=self.section01)
        self.article02 = ArticleFactory(parent=self.section01)

    def test_start_from_section_when_current_page_is_section(self):
        request = HttpRequest()
        request.path = '/admin/choose-page/'
        request.META['HTTP_REFERER'] = f'https://example.com/admin/pages/{self.section01.id}/edit/'
        pages = self.home_page.get_children()

        pages = limit_page_chooser(pages, request)

        self.assertEqual([i for i in pages.values_list('id', flat=True)], [self.section02.id, self.article02.id])

    def test_start_from_section_when_parent_page_is_section(self):
        request = HttpRequest()
        request.path = f'/admin/choose-page/{self.section01.id}/'
        pages = self.home_page.get_children()

        pages = limit_page_chooser(pages, request)

        self.assertEqual([i for i in pages.values_list('id', flat=True)], [self.section02.id, self.article02.id])

    def test_do_not_change_queryset_when_current_page_is_not_a_section(self):
        request = HttpRequest()
        request.path = '/admin/choose-page/'
        request.META['HTTP_REFERER'] = f'https://example.com/admin/pages/{self.home_page.id}/edit/'
        pages_before = self.home_page.get_children()

        pages_after = limit_page_chooser(pages_before, request)

        self.assertEqual(pages_after, pages_before)

    def test_do_not_change_queryset_when_parent_page_is_not_a_section(self):
        request = HttpRequest()
        request.path = f'/admin/choose-page/{self.home_page.id}/'
        pages_before = self.home_page.get_children()

        pages_after = limit_page_chooser(pages_before, request)

        self.assertEqual(pages_after, pages_before)


class HomePageFeaturedItemTest(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.home_page = self.site.root_page.specific
        self.section_index_page = SectionIndexFactory(parent=self.home_page)
        self.section = SectionFactory(parent=self.section_index_page)
        self.article = ArticleFactory(parent=self.section)
        self.poll = PollFactory(parent=self.section)
        self.survey = SurveyFactory(parent=self.section)
        self.quiz = QuizFactory(parent=self.section)

    def test_home_page_featured_item_with_empty_title(self):
        self.home_page.home_featured_content.append((
            'article', {
                'article': self.article,
                'display_section_title': True,
            }
        ))
        self.home_page.home_featured_content.append((
            'embedded_poll', {
                'poll': self.poll,
                'direct_display': False,
            }
        ))
        self.home_page.home_featured_content.append((
            'embedded_survey', {
                'survey': self.survey,
                'direct_display': False,
            }
        ))
        self.home_page.home_featured_content.append((
            'embedded_quiz', {
                'quiz': self.quiz,
                'direct_display': False,
            }
        ))
        self.home_page.save()

        response = self.client.get(self.home_page.url)
        parsed_response = BeautifulSoup(response.content)
        article_title = parsed_response.find("p", {"class": "article-title"}).text
        poll_title = parsed_response.find("div", {"class": "block-embedded_poll"}).find("p").findNext("p").text
        survey_title = parsed_response.find("div", {"class": "block-embedded_survey"}).find("p").findNext("p").text
        quiz_title = parsed_response.find("div", {"class": "block-embedded_quiz"}).find("p").findNext("p").text

        self.assertEqual(response.status_code, 200)
        self.assertEqual(article_title, self.home_page.home_featured_content[0].value['article'].title)
        self.assertEqual(poll_title, self.home_page.home_featured_content[1].value['poll'].title)
        self.assertEqual(survey_title, self.home_page.home_featured_content[2].value['survey'].title)
        self.assertEqual(quiz_title, self.home_page.home_featured_content[3].value['quiz'].title)

    def test_home_page_featured_item_with_new_title(self):
        self.home_page.home_featured_content.append((
            'article', {
                'title': 'new article title',
                'article': self.article,
                'display_section_title': True,
            }
        ))
        self.home_page.home_featured_content.append((
            'embedded_poll', {
                'title': 'new poll title',
                'poll': self.poll,
                'direct_display': False,
            }
        ))
        self.home_page.home_featured_content.append((
            'embedded_survey', {
                'title': 'new survey title',
                'survey': self.survey,
                'direct_display': False,
            }
        ))
        self.home_page.home_featured_content.append((
            'embedded_quiz', {
                'title': 'new quiz title',
                'quiz': self.quiz,
                'direct_display': False,
            }
        ))
        self.home_page.save()

        response = self.client.get(self.home_page.url)
        parsed_response = BeautifulSoup(response.content)
        article_title = parsed_response.find("p", {"class": "article-title"}).text
        poll_title = parsed_response.find("div", {"class": "block-embedded_poll"}).find("p").findNext("p").text
        survey_title = parsed_response.find("div", {"class": "block-embedded_survey"}).find("p").findNext("p").text
        quiz_title = parsed_response.find("div", {"class": "block-embedded_quiz"}).find("p").findNext("p").text

        self.assertEqual(response.status_code, 200)
        self.assertEqual(article_title, self.home_page.home_featured_content[0].value['title'])
        self.assertEqual(poll_title, self.home_page.home_featured_content[1].value['title'])
        self.assertEqual(survey_title, self.home_page.home_featured_content[2].value['title'])
        self.assertEqual(quiz_title, self.home_page.home_featured_content[3].value['title'])
