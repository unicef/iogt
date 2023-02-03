from django.test import TestCase
from django.http import HttpRequest
from translation_manager.models import TranslationEntry
from wagtail.core.models import Site
from wagtail_localize.operations import TranslationCreator

from home.wagtail_hooks import limit_page_chooser
from home.factories import SectionFactory, SectionIndexFactory, ArticleFactory, HomePageFactory, MediaFactory, LocaleFactory
from wagtail_factories import SiteFactory, PageFactory
from bs4 import BeautifulSoup

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


class MediaTranslationTest(TestCase):
    def setUp(self):
        root_page = PageFactory(parent=None)
        en_home_page = HomePageFactory(parent=root_page)
        SiteFactory(hostname='testserver', port=80, root_page=en_home_page)
        self.en_article = ArticleFactory(
            parent=en_home_page,
            body__0__media=MediaFactory(type='video'),
            body__1__media=MediaFactory(type='audio'),
        )

    def test_media_block_translation_of_english_language(self):
        response = self.client.get(self.en_article.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"If you cannot view the above video, you can instead <a href=\"{self.en_article.body[0].value.url}\" download>download it</a>", count=1)
        self.assertContains(response, f"If you cannot listen to the above audio, you can instead <a href=\"{self.en_article.body[1].value.url}\" download>download it</a>", count=1)

    def test_media_block_translation_of_bengali_language(self):
        bn_locale = LocaleFactory(language_code='bn')
        bn_translation_creator = TranslationCreator(user=None, target_locales=[bn_locale])
        bn_translation_creator.create_translations(self.en_article)
        bn_article = self.en_article.get_translation(bn_locale)

        TranslationEntry.objects.create(
            original="If you cannot view the above video, you can instead %(start_link)sdownload it%(end_link)s.",
            translation="উপরের ভিডিও দেখা না গেলে %(start_link)s এর পরিবর্তে এটা %(end_link)s ডাউনলোড করুন",
            language=bn_locale.language_code)
        TranslationEntry.objects.create(
            original="If you cannot listen to the above audio, you can instead %(start_link)sdownload it%(end_link)s.",
            translation="উপরের অডিও শুনতে না পেলে %(start_link)s এর পরিবর্তে এটা %(end_link)s ডাউনলোড করুন",
            language=bn_locale.language_code)

        response = self.client.get(bn_article.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"উপরের ভিডিও দেখা না গেলে <a href=\"{self.en_article.body[0].value.url}\" download> এর পরিবর্তে এটা </a> ডাউনলোড করুন", count=1)
        self.assertContains(response, f"উপরের অডিও শুনতে না পেলে <a href=\"{self.en_article.body[1].value.url}\" download> এর পরিবর্তে এটা </a> ডাউনলোড করুন", count=1)


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
        self.assertEqual(article_title, "new article title")
        self.assertEqual(poll_title, "new poll title")
        self.assertEqual(survey_title, "new survey title")
        self.assertEqual(quiz_title, "new quiz title")
