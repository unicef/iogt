from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from wagtail.core.models import Site
from wagtail_factories import SiteFactory

from home.factories import HomePageFactory
from iogt_users.factories import UserFactory
from questionnaires.factories import PollFactory, SurveyFactory, QuizFactory


class QuestionnairesListAPIViewTests(TestCase):
    def setUp(self):
        self.url = reverse('questionnaires_list')
        self.user = UserFactory()

        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

    def test_questionnaires_list(self):
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01')
        poll_02 = PollFactory(parent=self.home_page, title='Poll 02')
        poll_03 = PollFactory(parent=self.home_page, title='Poll 03')
        survey_01 = SurveyFactory(parent=self.home_page, title='Survey 01')
        survey_02 = SurveyFactory(parent=self.home_page, title='Survey 02')
        survey_03 = SurveyFactory(parent=self.home_page, title='Survey 03')
        quiz_01 = QuizFactory(parent=self.home_page, title='Quiz 01')
        quiz_02 = QuizFactory(parent=self.home_page, title='Quiz 02')
        quiz_03 = QuizFactory(parent=self.home_page, title='Quiz 03')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)
        self.assertEqual(response.data['results'][2]['title'], poll_03.title)
        self.assertEqual(response.data['results'][3]['title'], quiz_01.title)
        self.assertEqual(response.data['results'][4]['title'], quiz_02.title)
        self.assertEqual(response.data['results'][5]['title'], quiz_03.title)
        self.assertEqual(response.data['results'][6]['title'], survey_01.title)
        self.assertEqual(response.data['results'][7]['title'], survey_02.title)
        self.assertEqual(response.data['results'][8]['title'], survey_03.title)

    def test_questionnaires_list_type_filter(self):
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01')
        poll_02 = PollFactory(parent=self.home_page, title='Poll 02')
        poll_03 = PollFactory(parent=self.home_page, title='Poll 03')
        survey_01 = SurveyFactory(parent=self.home_page, title='Survey 01')
        survey_02 = SurveyFactory(parent=self.home_page, title='Survey 02')
        survey_03 = SurveyFactory(parent=self.home_page, title='Survey 03')
        quiz_01 = QuizFactory(parent=self.home_page, title='Quiz 01')
        quiz_02 = QuizFactory(parent=self.home_page, title='Quiz 02')
        quiz_03 = QuizFactory(parent=self.home_page, title='Quiz 03')

        response = self.client.get(f'{self.url}?type=poll')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)
        self.assertEqual(response.data['results'][2]['title'], poll_03.title)

        response = self.client.get(f'{self.url}?type=survey')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], survey_01.title)
        self.assertEqual(response.data['results'][1]['title'], survey_02.title)
        self.assertEqual(response.data['results'][2]['title'], survey_03.title)

        response = self.client.get(f'{self.url}?type=quiz')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], quiz_01.title)
        self.assertEqual(response.data['results'][1]['title'], quiz_02.title)
        self.assertEqual(response.data['results'][2]['title'], quiz_03.title)

    def test_questionnaires_list_published_at_filter(self):
        current_datetime = timezone.now()
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01', last_published_at=current_datetime)
        poll_02 = PollFactory(parent=self.home_page, title='Poll 02', last_published_at=current_datetime - timedelta(days=1))
        poll_03 = PollFactory(parent=self.home_page, title='Poll 03', last_published_at=current_datetime - timedelta(days=2))

        response = self.client.get(f'{self.url}?published_at_start={(current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)

        response = self.client.get(f'{self.url}?published_at_end={(current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_02.title)
        self.assertEqual(response.data['results'][1]['title'], poll_03.title)

    def test_questionnaires_list_page_size(self):
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01')
        poll_02 = PollFactory(parent=self.home_page, title='Poll 02')
        poll_03 = PollFactory(parent=self.home_page, title='Poll 03')
        survey_01 = SurveyFactory(parent=self.home_page, title='Survey 01')
        survey_02 = SurveyFactory(parent=self.home_page, title='Survey 02')
        survey_03 = SurveyFactory(parent=self.home_page, title='Survey 03')
        quiz_01 = QuizFactory(parent=self.home_page, title='Quiz 01')
        quiz_02 = QuizFactory(parent=self.home_page, title='Quiz 02')
        quiz_03 = QuizFactory(parent=self.home_page, title='Quiz 03')

        response = self.client.get(f'{self.url}?page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertEqual(response.data['next'], 'http://testserver/questionnaires/list/?page=2&page_size=3')
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)
        self.assertEqual(response.data['results'][2]['title'], poll_03.title)

        response = self.client.get(f'{self.url}?page=2&page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertEqual(response.data['next'], 'http://testserver/questionnaires/list/?page=3&page_size=3')
        self.assertEqual(response.data['previous'], 'http://testserver/questionnaires/list/?page_size=3')
        self.assertEqual(response.data['results'][0]['title'], quiz_01.title)
        self.assertEqual(response.data['results'][1]['title'], quiz_02.title)
        self.assertEqual(response.data['results'][2]['title'], quiz_03.title)

        response = self.client.get(f'{self.url}?page=3&page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertIsNone(response.data['next'])
        self.assertEqual(response.data['previous'], 'http://testserver/questionnaires/list/?page=2&page_size=3')
        self.assertEqual(response.data['results'][0]['title'], survey_01.title)
        self.assertEqual(response.data['results'][1]['title'], survey_02.title)
        self.assertEqual(response.data['results'][2]['title'], survey_03.title)
