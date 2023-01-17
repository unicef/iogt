import datetime
import io
import json
from datetime import timedelta

import pytz
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django_webtest import WebTest
from openpyxl import load_workbook
from rest_framework import status
from rest_framework.test import APIClient
from wagtail.core.models import Site, Page
from wagtail_factories import SiteFactory
from webtest.forms import Hidden

from home.factories import HomePageFactory
from iogt_users.factories import (
    UserFactory,
    GroupFactory,
    GroupPagePermissionFactory,
    AdminUserFactory,
)
from questionnaires.factories import (
    PollFactory,
    SurveyFactory,
    QuizFactory,
    PollFormFieldFactory,
    SurveyFormFieldFactory,
    QuizFormFieldFactory,
    UserSubmissionFactory,
    PollIndexPageFactory,
)


class QuestionnairesListAPIViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.group = GroupFactory(name='questionnaires')
        self.user.groups.add(self.group)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('questionnaires_list')

        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

    def test_questionnaires_list(self):
        current_datetime = timezone.now()
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01', last_published_at=current_datetime)
        poll_02 = PollFactory(
            parent=self.home_page, title='Poll 02', last_published_at=current_datetime - timedelta(days=1))
        poll_03 = PollFactory(
            parent=self.home_page, title='Poll 03', last_published_at=current_datetime - timedelta(days=2))
        survey_01 = SurveyFactory(
            parent=self.home_page, title='Survey 01', last_published_at=current_datetime - timedelta(days=3))
        survey_02 = SurveyFactory(
            parent=self.home_page, title='Survey 02', last_published_at=current_datetime - timedelta(days=4))
        survey_03 = SurveyFactory(
            parent=self.home_page, title='Survey 03', last_published_at=current_datetime - timedelta(days=5))
        quiz_01 = QuizFactory(
            parent=self.home_page, title='Quiz 01', last_published_at=current_datetime - timedelta(days=6))
        quiz_02 = QuizFactory(
            parent=self.home_page, title='Quiz 02', last_published_at=current_datetime - timedelta(days=7))
        quiz_03 = QuizFactory(
            parent=self.home_page, title='Quiz 03', last_published_at=current_datetime - timedelta(days=8))
        GroupPagePermissionFactory(group=self.group, page=poll_01)
        GroupPagePermissionFactory(group=self.group, page=poll_02)
        GroupPagePermissionFactory(group=self.group, page=poll_03)
        GroupPagePermissionFactory(group=self.group, page=survey_01)
        GroupPagePermissionFactory(group=self.group, page=survey_02)
        GroupPagePermissionFactory(group=self.group, page=survey_03)
        GroupPagePermissionFactory(group=self.group, page=quiz_01)
        GroupPagePermissionFactory(group=self.group, page=quiz_02)
        GroupPagePermissionFactory(group=self.group, page=quiz_03)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)
        self.assertEqual(response.data['results'][2]['title'], poll_03.title)
        self.assertEqual(response.data['results'][3]['title'], survey_01.title)
        self.assertEqual(response.data['results'][4]['title'], survey_02.title)
        self.assertEqual(response.data['results'][5]['title'], survey_03.title)
        self.assertEqual(response.data['results'][6]['title'], quiz_01.title)
        self.assertEqual(response.data['results'][7]['title'], quiz_02.title)
        self.assertEqual(response.data['results'][8]['title'], quiz_03.title)

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
        GroupPagePermissionFactory(group=self.group, page=poll_01)
        GroupPagePermissionFactory(group=self.group, page=poll_02)
        GroupPagePermissionFactory(group=self.group, page=poll_03)
        GroupPagePermissionFactory(group=self.group, page=survey_01)
        GroupPagePermissionFactory(group=self.group, page=survey_02)
        GroupPagePermissionFactory(group=self.group, page=survey_03)
        GroupPagePermissionFactory(group=self.group, page=quiz_01)
        GroupPagePermissionFactory(group=self.group, page=quiz_02)
        GroupPagePermissionFactory(group=self.group, page=quiz_03)

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

    def test_questionnaires_list_last_published_at_filter(self):
        current_datetime = timezone.now()
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01', last_published_at=current_datetime)
        poll_02 = PollFactory(parent=self.home_page, title='Poll 02', last_published_at=current_datetime - timedelta(days=1))
        poll_03 = PollFactory(parent=self.home_page, title='Poll 03', last_published_at=current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=poll_01)
        GroupPagePermissionFactory(group=self.group, page=poll_02)
        GroupPagePermissionFactory(group=self.group, page=poll_03)

        response = self.client.get(f'{self.url}?last_published_at_start={(current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)

        response = self.client.get(f'{self.url}?last_published_at_end={(current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_02.title)
        self.assertEqual(response.data['results'][1]['title'], poll_03.title)

    def test_questionnaires_list_page_size(self):
        current_datetime = timezone.now()
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01', last_published_at=current_datetime)
        poll_02 = PollFactory(
            parent=self.home_page, title='Poll 02', last_published_at=current_datetime - timedelta(days=1))
        poll_03 = PollFactory(
            parent=self.home_page, title='Poll 03', last_published_at=current_datetime - timedelta(days=2))
        survey_01 = SurveyFactory(
            parent=self.home_page, title='Survey 01', last_published_at=current_datetime - timedelta(days=3))
        survey_02 = SurveyFactory(
            parent=self.home_page, title='Survey 02', last_published_at=current_datetime - timedelta(days=4))
        survey_03 = SurveyFactory(
            parent=self.home_page, title='Survey 03', last_published_at=current_datetime - timedelta(days=5))
        quiz_01 = QuizFactory(
            parent=self.home_page, title='Quiz 01', last_published_at=current_datetime - timedelta(days=6))
        quiz_02 = QuizFactory(
            parent=self.home_page, title='Quiz 02', last_published_at=current_datetime - timedelta(days=7))
        quiz_03 = QuizFactory(
            parent=self.home_page, title='Quiz 03', last_published_at=current_datetime - timedelta(days=8))
        GroupPagePermissionFactory(group=self.group, page=poll_01)
        GroupPagePermissionFactory(group=self.group, page=poll_02)
        GroupPagePermissionFactory(group=self.group, page=poll_03)
        GroupPagePermissionFactory(group=self.group, page=survey_01)
        GroupPagePermissionFactory(group=self.group, page=survey_02)
        GroupPagePermissionFactory(group=self.group, page=survey_03)
        GroupPagePermissionFactory(group=self.group, page=quiz_01)
        GroupPagePermissionFactory(group=self.group, page=quiz_02)
        GroupPagePermissionFactory(group=self.group, page=quiz_03)

        response = self.client.get(f'{self.url}?page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertEqual(response.data['next'], 'http://testserver/api/v1/questionnaires/?page=2&page_size=3')
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)
        self.assertEqual(response.data['results'][2]['title'], poll_03.title)

        response = self.client.get(f'{self.url}?page=2&page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertEqual(response.data['next'], 'http://testserver/api/v1/questionnaires/?page=3&page_size=3')
        self.assertEqual(response.data['previous'], 'http://testserver/api/v1/questionnaires/?page_size=3')
        self.assertEqual(response.data['results'][0]['title'], survey_01.title)
        self.assertEqual(response.data['results'][1]['title'], survey_02.title)
        self.assertEqual(response.data['results'][2]['title'], survey_03.title)

        response = self.client.get(f'{self.url}?page=3&page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertIsNone(response.data['next'])
        self.assertEqual(response.data['previous'], 'http://testserver/api/v1/questionnaires/?page=2&page_size=3')
        self.assertEqual(response.data['results'][0]['title'], quiz_01.title)
        self.assertEqual(response.data['results'][1]['title'], quiz_02.title)
        self.assertEqual(response.data['results'][2]['title'], quiz_03.title)

    def test_questionnaires_list_page_permission(self):
        current_datetime = timezone.now()
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01', last_published_at=current_datetime)
        poll_02 = PollFactory(
            parent=self.home_page, title='Poll 02', last_published_at=current_datetime - timedelta(days=1))
        poll_03 = PollFactory(
            parent=self.home_page, title='Poll 03', last_published_at=current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=poll_01)
        GroupPagePermissionFactory(group=self.group, page=poll_02)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['title'], poll_01.title)
        self.assertEqual(response.data['results'][1]['title'], poll_02.title)


class QuestionnaireDetailAPIViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.group = GroupFactory(name='questionnaires')
        self.user.groups.add(self.group)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = 'questionnaire_detail'

        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

    def test_poll_detail(self):
        poll = PollFactory(parent=self.home_page)
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        response = self.client.get(reverse(self.url, kwargs={'pk': poll.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], poll.id)
        self.assertEqual(response.data['title'], poll.title)
        self.assertEqual(response.data['live'], poll.live)
        self.assertEqual(response.data['url'], poll.full_url)
        self.assertIsNotNone(response.data['last_published_at'])
        self.assertEqual(response.data['allow_anonymous_submissions'], poll.allow_anonymous_submissions)
        self.assertEqual(response.data['allow_multiple_submissions'], poll.allow_multiple_submissions)
        self.assertEqual(response.data['show_results'], poll.show_results)
        self.assertEqual(response.data['result_as_percentage'], poll.result_as_percentage)
        self.assertEqual(response.data['randomise_options'], poll.randomise_options)
        self.assertEqual(response.data['show_results_with_no_votes'], poll.show_results_with_no_votes)
        self.assertEqual(response.data['submit_button_text'], poll.submit_button_text)
        self.assertEqual(response.data['direct_display'], poll.direct_display)
        self.assertEqual(response.data['index_page_description'], poll.index_page_description)
        self.assertEqual(response.data['index_page_description_line_2'], poll.index_page_description_line_2)
        self.assertEqual(response.data['questions'][0]['id'], poll_question.id)
        self.assertEqual(response.data['questions'][0]['label'], poll_question.label)
        self.assertEqual(response.data['questions'][0]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['questions'][0]['help_text'], poll_question.help_text)
        self.assertEqual(response.data['questions'][0]['required'], poll_question.required)
        self.assertEqual(response.data['questions'][0]['field_type'], poll_question.field_type)
        self.assertEqual(response.data['questions'][0]['choices'][0], 'c1')
        self.assertEqual(response.data['questions'][0]['choices'][1], 'c2')
        self.assertEqual(response.data['questions'][0]['choices'][2], 'c3')
        self.assertEqual(response.data['questions'][0]['default_value'], [poll_question.default_value])
        self.assertEqual(response.data['questions'][0]['admin_label'], poll_question.admin_label)

    def test_survey_detail(self):
        survey = SurveyFactory(parent=self.home_page)
        GroupPagePermissionFactory(group=self.group, page=survey)
        skip_logic = json.dumps(
            [
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "c1",
                        "skip_logic": "next",
                        "question": None
                    }
                },
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "c2",
                        "skip_logic": "next",
                        "question": None
                    }
                },
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "c3",
                        "skip_logic": "next",
                        "question": None
                    }
                }
            ]
        )
        survey_question = SurveyFormFieldFactory(
            page=survey, field_type='checkboxes', skip_logic=skip_logic, default_value='c2')

        response = self.client.get(reverse(self.url, kwargs={'pk': survey.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], survey.id)
        self.assertEqual(response.data['title'], survey.title)
        self.assertEqual(response.data['live'], survey.live)
        self.assertEqual(response.data['url'], survey.full_url)
        self.assertIsNotNone(response.data['last_published_at'])
        self.assertEqual(response.data['allow_anonymous_submissions'], survey.allow_anonymous_submissions)
        self.assertEqual(response.data['allow_multiple_submissions'], survey.allow_multiple_submissions)
        self.assertEqual(response.data['submit_button_text'], survey.submit_button_text)
        self.assertEqual(response.data['multi_step'], survey.multi_step)
        self.assertEqual(response.data['direct_display'], survey.direct_display)
        self.assertEqual(response.data['index_page_description'], survey.index_page_description)
        self.assertEqual(response.data['index_page_description_line_2'], survey.index_page_description_line_2)
        self.assertEqual(response.data['questions'][0]['id'], survey_question.id)
        self.assertEqual(response.data['questions'][0]['label'], survey_question.label)
        self.assertEqual(response.data['questions'][0]['clean_name'], survey_question.clean_name)
        self.assertEqual(response.data['questions'][0]['help_text'], survey_question.help_text)
        self.assertEqual(response.data['questions'][0]['required'], survey_question.required)
        self.assertEqual(response.data['questions'][0]['field_type'], survey_question.field_type)
        self.assertEqual(response.data['questions'][0]['skip_logic'][0]['type'], 'skip_logic')
        self.assertEqual(response.data['questions'][0]['skip_logic'][0]['value']['choice'], 'c1')
        self.assertEqual(response.data['questions'][0]['skip_logic'][0]['value']['skip_logic'], 'next')
        self.assertEqual(response.data['questions'][0]['skip_logic'][0]['value']['question'], None)
        self.assertEqual(response.data['questions'][0]['skip_logic'][1]['type'], 'skip_logic')
        self.assertEqual(response.data['questions'][0]['skip_logic'][1]['value']['choice'], 'c2')
        self.assertEqual(response.data['questions'][0]['skip_logic'][1]['value']['skip_logic'], 'next')
        self.assertEqual(response.data['questions'][0]['skip_logic'][1]['value']['question'], None)
        self.assertEqual(response.data['questions'][0]['skip_logic'][2]['type'], 'skip_logic')
        self.assertEqual(response.data['questions'][0]['skip_logic'][2]['value']['choice'], 'c3')
        self.assertEqual(response.data['questions'][0]['skip_logic'][2]['value']['skip_logic'], 'next')
        self.assertEqual(response.data['questions'][0]['skip_logic'][2]['value']['question'], None)
        self.assertEqual(response.data['questions'][0]['default_value'], [survey_question.default_value])
        self.assertEqual(response.data['questions'][0]['admin_label'], survey_question.admin_label)

    def test_quiz_detail(self):
        quiz = QuizFactory(parent=self.home_page)
        GroupPagePermissionFactory(group=self.group, page=quiz)
        quiz_question = QuizFormFieldFactory(
            page=quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        response = self.client.get(reverse(self.url, kwargs={'pk': quiz.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], quiz.id)
        self.assertEqual(response.data['title'], quiz.title)
        self.assertEqual(response.data['live'], quiz.live)
        self.assertEqual(response.data['url'], quiz.full_url)
        self.assertIsNotNone(response.data['last_published_at'])
        self.assertEqual(response.data['allow_anonymous_submissions'], quiz.allow_anonymous_submissions)
        self.assertEqual(response.data['allow_multiple_submissions'], quiz.allow_multiple_submissions)
        self.assertEqual(response.data['submit_button_text'], quiz.submit_button_text)
        self.assertEqual(response.data['multi_step'], quiz.multi_step)
        self.assertEqual(response.data['direct_display'], quiz.direct_display)
        self.assertEqual(response.data['index_page_description'], quiz.index_page_description)
        self.assertEqual(response.data['index_page_description_line_2'], quiz.index_page_description_line_2)
        self.assertEqual(response.data['questions'][0]['id'], quiz_question.id)
        self.assertEqual(response.data['questions'][0]['label'], quiz_question.label)
        self.assertEqual(response.data['questions'][0]['clean_name'], quiz_question.clean_name)
        self.assertEqual(response.data['questions'][0]['help_text'], quiz_question.help_text)
        self.assertEqual(response.data['questions'][0]['required'], quiz_question.required)
        self.assertEqual(response.data['questions'][0]['field_type'], quiz_question.field_type)
        self.assertEqual(response.data['questions'][0]['choices'][0], 'c1')
        self.assertEqual(response.data['questions'][0]['choices'][1], 'c2')
        self.assertEqual(response.data['questions'][0]['choices'][2], 'c3')
        self.assertEqual(response.data['questions'][0]['default_value'], [quiz_question.default_value])
        self.assertEqual(response.data['questions'][0]['correct_answer'], [quiz_question.correct_answer])
        self.assertEqual(response.data['questions'][0]['feedback'], quiz_question.feedback)
        self.assertEqual(response.data['questions'][0]['admin_label'], quiz_question.admin_label)

    def test_questionnaires_detail_page_permission(self):
        poll = PollFactory(parent=self.home_page)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        response = self.client.get(reverse(self.url, kwargs={'pk': poll.id}))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)


class QuestionnaireSubmissionsAPIViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.group = GroupFactory(name='questionnaires')
        self.user.groups.add(self.group)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = 'questionnaire_submissions'

        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

    def test_questionnaire_submission_list(self):
        current_datetime = timezone.now()
        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=3))
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        user_02 = UserFactory()
        form_data_02 = json.dumps({
            poll_question.clean_name: [
                'c2',
                'c3',
            ],
        })
        user_submission_02 = UserSubmissionFactory(page=poll, user=user_02, form_data=form_data_02)
        user_submission_02.submit_time = current_datetime - timedelta(days=1)
        user_submission_02.save()

        user_03 = UserFactory()
        form_data_03 = json.dumps({
            poll_question.clean_name: [
                'c3',
            ],
        })
        user_submission_03 = UserSubmissionFactory(page=poll, user=user_03, form_data=form_data_03)
        user_submission_03.submit_time = current_datetime - timedelta(days=2)
        user_submission_03.save()

        response = self.client.get(reverse(self.url, kwargs={'pk': poll.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_01.id)
        self.assertEqual(response.data['results'][0]['user'], user_01.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c1'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][1]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['user_answer'], ['c2', 'c3'])
        self.assertEqual(response.data['results'][2]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][2]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][2]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][2]['submit_time'])
        self.assertEqual(response.data['results'][2]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][2]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][2]['submission'][0][poll_question.admin_label]['user_answer'], ['c3'])

    def test_questionnaire_submission_list_submit_time_filter(self):
        current_datetime = timezone.now()
        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=3))
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        user_02 = UserFactory()
        form_data_02 = json.dumps({
            poll_question.clean_name: [
                'c2',
                'c3',
            ],
        })
        user_submission_02 = UserSubmissionFactory(page=poll, user=user_02, form_data=form_data_02)
        user_submission_02.submit_time = current_datetime - timedelta(days=1)
        user_submission_02.save()

        user_03 = UserFactory()
        form_data_03 = json.dumps({
            poll_question.clean_name: [
                'c3',
            ],
        })
        user_submission_03 = UserSubmissionFactory(page=poll, user=user_03, form_data=form_data_03)
        user_submission_03.submit_time = current_datetime - timedelta(days=2)
        user_submission_03.save()

        response = self.client.get(
            f"{reverse(self.url, kwargs={'pk': poll.id})}?submit_time_start={(current_datetime - timedelta(days=1)).date()}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_01.id)
        self.assertEqual(response.data['results'][0]['user'], user_01.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c1'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][1]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['user_answer'], ['c2', 'c3'])

        response = self.client.get(
            f"{reverse(self.url, kwargs={'pk': poll.id})}?submit_time_end={(current_datetime - timedelta(days=1)).date()}")

        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][0]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c2', 'c3'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['user_answer'], ['c3'])

    def test_questionnaire_submission_list_user_ids_filter(self):
        current_datetime = timezone.now()
        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=3))
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(
            page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', admin_label='Q1')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        user_02 = UserFactory()
        form_data_02 = json.dumps({
            poll_question.clean_name: [
                'c2',
                'c3',
            ],
        })
        user_submission_02 = UserSubmissionFactory(page=poll, user=user_02, form_data=form_data_02)
        user_submission_02.submit_time = current_datetime - timedelta(days=1)
        user_submission_02.save()

        user_03 = UserFactory()
        form_data_03 = json.dumps({
            poll_question.clean_name: [
                'c3',
            ],
        })
        user_submission_03 = UserSubmissionFactory(page=poll, user=user_03, form_data=form_data_03)
        user_submission_03.submit_time = current_datetime - timedelta(days=2)
        user_submission_03.save()

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?user_ids={user_01.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_01.id)
        self.assertEqual(response.data['results'][0]['user'], user_01.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c1'])

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?user_ids={user_02.id},{user_03.id}")

        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][0]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c2', 'c3'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][1]['submission'][0][poll_question.admin_label]['user_answer'], ['c3'])

    def test_questionnaire_submission_list_page_size(self):
        current_datetime = timezone.now()
        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=3))
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        user_02 = UserFactory()
        form_data_02 = json.dumps({
            poll_question.clean_name: [
                'c2',
                'c3',
            ],
        })
        user_submission_02 = UserSubmissionFactory(page=poll, user=user_02, form_data=form_data_02)
        user_submission_02.submit_time = current_datetime - timedelta(days=1)
        user_submission_02.save()

        user_03 = UserFactory()
        form_data_03 = json.dumps({
            poll_question.clean_name: [
                'c3',
            ],
        })
        user_submission_03 = UserSubmissionFactory(page=poll, user=user_03, form_data=form_data_03)
        user_submission_03.submit_time = current_datetime - timedelta(days=2)
        user_submission_03.save()

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?page_size=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(
            response.data['next'], f'http://testserver/api/v1/questionnaires/{poll.id}/submissions/?page=2&page_size=1')
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_01.id)
        self.assertEqual(response.data['results'][0]['user'], user_01.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c1'])

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?page=2&page_size=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(
            response.data['next'], f'http://testserver/api/v1/questionnaires/{poll.id}/submissions/?page=3&page_size=1')
        self.assertEqual(
            response.data['previous'], f'http://testserver/api/v1/questionnaires/{poll.id}/submissions/?page_size=1')
        self.assertEqual(response.data['results'][0]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][0]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c2', 'c3'])

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?page=3&page_size=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIsNone(response.data['next'])
        self.assertEqual(
            response.data['previous'], f'http://testserver/api/v1/questionnaires/{poll.id}/submissions/?page=2&page_size=1')
        self.assertEqual(response.data['results'][0]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][0]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0][poll_question.admin_label]['user_answer'], ['c3'])

    def test_questionnaires_detail_page_permission(self):
        current_datetime = timezone.now()
        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=3))
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        response = self.client.get(reverse(self.url, kwargs={'pk': poll.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class FormDataPerUserAdminTests(TestCase):
    def setUp(self):
        self.group = GroupFactory(name='questionnaires')
        self.admin_access_permission = Permission.objects.get(codename='access_admin')
        self.group.permissions.add(self.admin_access_permission)
        self.staff_user = UserFactory()
        self.staff_user.groups.add(self.group)
        self.client.force_login(self.staff_user)
        self.url = reverse('form_data_per_user')
        self.current_datetime = datetime.datetime(
            year=2022, month=9, day=1, hour=23, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

        self.poll = PollFactory(parent=self.home_page, last_published_at=self.current_datetime)
        GroupPagePermissionFactory(group=self.group, page=self.poll)
        self.poll_question = PollFormFieldFactory(page=self.poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        self.survey = SurveyFactory(parent=self.home_page, title='Survey 01', last_published_at=self.current_datetime - timedelta(days=1))
        GroupPagePermissionFactory(group=self.group, page=self.survey)
        self.skip_logic = json.dumps(
            [
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "c1",
                        "skip_logic": "next",
                        "question": None
                    }
                },
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "c2",
                        "skip_logic": "next",
                        "question": None
                    }
                },
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "c3",
                        "skip_logic": "next",
                        "question": None
                    }
                }
            ]
        )
        self.survey_question = SurveyFormFieldFactory(
            page=self.survey, label='Question 01', admin_label='Q 01', field_type='checkboxes',
            skip_logic=self.skip_logic, default_value='c2')

        self.quiz = QuizFactory(parent=self.home_page, last_published_at=self.current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=self.quiz)
        self.quiz_question = QuizFormFieldFactory(
            page=self.quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        self.user_01 = UserFactory(username='test')
        form_data_01 = json.dumps({
            self.poll_question.clean_name: [
                'c1',
            ],
        })
        self.user_submission_01 = UserSubmissionFactory(page=self.poll, user=self.user_01, form_data=form_data_01)
        self.user_submission_01.submit_time = self.current_datetime
        self.user_submission_01.save()

        form_data_02 = json.dumps({
            self.survey_question.clean_name: [
                'c2',
            ],
        })
        self.user_submission_02 = UserSubmissionFactory(page=self.survey, user=self.user_01, form_data=form_data_02)
        self.user_submission_02.submit_time = self.current_datetime - timedelta(days=1)
        self.user_submission_02.save()

        form_data_03 = json.dumps({
            self.quiz_question.clean_name: [
                'c3',
            ],
        })
        self.user_submission_03 = UserSubmissionFactory(page=self.quiz, user=self.user_01, form_data=form_data_03)
        self.user_submission_03.submit_time = self.current_datetime - timedelta(days=2)
        self.user_submission_03.save()

        self.user_02 = UserFactory()
        form_data_04 = json.dumps({
            self.quiz_question.clean_name: [
                'c3',
            ],
        })
        self.user_submission_04 = UserSubmissionFactory(page=self.quiz, user=self.user_02, form_data=form_data_04)
        self.user_submission_04.submit_time = self.current_datetime - timedelta(days=2)
        self.user_submission_04.save()

    def test_listing(self):
        response = self.client.get(f'{self.url}?user_id={self.user_01.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 3)
        self.assertEqual(response.context['form_pages'][0].title, self.poll.title)
        self.assertEqual(response.context['form_pages'][1].title, self.survey.title)
        self.assertEqual(response.context['form_pages'][2].title, self.quiz.title)

        response = self.client.get(f'{self.url}?user_id={self.user_02.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 1)
        self.assertEqual(response.context['form_pages'][0].title, self.quiz.title)

    def test_date_range_filter(self):
        response = self.client.get(f'{self.url}?user_id={self.user_01.id}&date_from={(self.current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 2)
        self.assertEqual(response.context['form_pages'][0].title, self.poll.title)
        self.assertEqual(response.context['form_pages'][1].title, self.survey.title)

        response = self.client.get(f'{self.url}?user_id={self.user_01.id}&date_to={(self.current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 2)
        self.assertEqual(response.context['form_pages'][0].title, self.survey.title)
        self.assertEqual(response.context['form_pages'][1].title, self.quiz.title)

        response = self.client.get(f'{self.url}?user_id={self.user_01.id}&date_from={(self.current_datetime - timedelta(days=1)).date()}&date_to={(self.current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 1)
        self.assertEqual(response.context['form_pages'][0].title, self.survey.title)

    def test_export_page_ids_filter(self):
        response = self.client.get(f'{self.url}?user_id={self.user_01.id}&export=csv&page_ids={self.poll.id},{self.quiz.id}')

        byte_response = b''
        for stream in response.streaming_content:
            byte_response += stream
        expected_response = \
            f'ID,Name,Submission Date,Field,Value\r\n' \
            f'{self.user_submission_01.id},{self.poll.title},{self.user_submission_01.submit_time},User,{self.user_01.username}\r\n' \
            f'{self.user_submission_01.id},{self.poll.title},{self.user_submission_01.submit_time},URL,{self.poll.full_url}\r\n' \
            f'{self.user_submission_01.id},{self.poll.title},{self.user_submission_01.submit_time},{self.poll_question.clean_name},c1\r\n' \
            f'{self.user_submission_03.id},{self.quiz.title},{self.user_submission_03.submit_time},User,{self.user_01.username}\r\n' \
            f'{self.user_submission_03.id},{self.quiz.title},{self.user_submission_03.submit_time},URL,{self.quiz.full_url}\r\n' \
            f'{self.user_submission_03.id},{self.quiz.title},{self.user_submission_03.submit_time},{self.quiz_question.clean_name},c3\r\n'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(byte_response.decode(), expected_response)

    def test_csv_export(self):
        response = self.client.get(f'{self.url}?user_id={self.user_01.id}&export=csv')

        byte_response = b''
        for stream in response.streaming_content:
            byte_response += stream
        expected_response = \
            f'ID,Name,Submission Date,Field,Value\r\n' \
            f'{self.user_submission_01.id},{self.poll.title},{self.user_submission_01.submit_time},User,{self.user_01.username}\r\n' \
            f'{self.user_submission_01.id},{self.poll.title},{self.user_submission_01.submit_time},URL,{self.poll.full_url}\r\n' \
            f'{self.user_submission_01.id},{self.poll.title},{self.user_submission_01.submit_time},{self.poll_question.admin_label},c1\r\n' \
            f'{self.user_submission_02.id},{self.survey.title},{self.user_submission_02.submit_time},User,{self.user_01.username}\r\n' \
            f'{self.user_submission_02.id},{self.survey.title},{self.user_submission_02.submit_time},URL,{self.survey.full_url}\r\n' \
            f'{self.user_submission_02.id},{self.survey.title},{self.user_submission_02.submit_time},{self.survey_question.admin_label},c2\r\n' \
            f'{self.user_submission_03.id},{self.quiz.title},{self.user_submission_03.submit_time},User,{self.user_01.username}\r\n' \
            f'{self.user_submission_03.id},{self.quiz.title},{self.user_submission_03.submit_time},URL,{self.quiz.full_url}\r\n' \
            f'{self.user_submission_03.id},{self.quiz.title},{self.user_submission_03.submit_time},{self.quiz_question.admin_label},c3\r\n'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(byte_response.decode(), expected_response)

    def test_xlsx_export(self):
        response = self.client.get(f'{self.url}?user_id={self.user_01.id}&export=xlsx')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sheet = load_workbook(io.BytesIO(response.content)).active
        expected_response = {
            'A': {
                1: 'ID',
                2: f'{self.user_submission_01.id}',
                3: f'{self.user_submission_01.id}',
                4: f'{self.user_submission_01.id}',
                5: f'{self.user_submission_02.id}',
                6: f'{self.user_submission_02.id}',
                7: f'{self.user_submission_02.id}',
                8: f'{self.user_submission_03.id}',
                9: f'{self.user_submission_03.id}',
                10: f'{self.user_submission_03.id}',
            },
            'B': {
                1: 'Name',
                2: self.poll.title,
                3: self.poll.title,
                4: self.poll.title,
                5: self.survey.title,
                6: self.survey.title,
                7: self.survey.title,
                8: self.quiz.title,
                9: self.quiz.title,
                10: self.quiz.title,
            },
            'C': {
                1: 'Submission Date',
                2: self.user_submission_01.submit_time,
                3: self.user_submission_01.submit_time,
                4: self.user_submission_01.submit_time,
                5: self.user_submission_02.submit_time,
                6: self.user_submission_02.submit_time,
                7: self.user_submission_02.submit_time,
                8: self.user_submission_03.submit_time,
                9: self.user_submission_03.submit_time,
                10: self.user_submission_03.submit_time,
            },
            'D': {
                1: 'Field',
                2: 'User',
                3: 'URL',
                4: self.poll_question.admin_label,
                5: 'User',
                6: 'URL',
                7: self.survey_question.admin_label,
                8: 'User',
                9: 'URL',
                10: self.quiz_question.admin_label,
            },
            'E': {
                1: 'Value',
                2: self.user_01.username,
                3: self.poll.full_url,
                4: 'c1',
                5: self.user_01.username,
                6: self.survey.full_url,
                7: 'c2',
                8: self.user_01.username,
                9: self.quiz.full_url,
                10: 'c3',
            },
        }

        for row in [1, 2, 3, 4, 5, 6, 7]:
            for column in ['A', 'B', 'C', 'D', 'E']:
                value = sheet[f'{column}{row}'].value
                if isinstance(value, datetime.datetime):
                    value = value.replace(tzinfo=pytz.UTC)
                self.assertEqual(value, expected_response[column][row])

    def test_page_permission(self):
        quiz = QuizFactory(parent=self.home_page, last_published_at=self.current_datetime - timedelta(days=2))
        quiz_question = QuizFormFieldFactory(
            page=quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        form_data_04 = json.dumps({
            quiz_question.clean_name: [
                'c3',
            ],
        })
        UserSubmissionFactory(page=quiz, user=self.user_01, form_data=form_data_04)

        response = self.client.get(f'{self.url}?user_id={self.user_01.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 3)
        self.assertEqual(response.context['form_pages'][0].title, self.poll.title)
        self.assertEqual(response.context['form_pages'][1].title, self.survey.title)
        self.assertEqual(response.context['form_pages'][2].title, self.quiz.title)

    def test_csv_export_with_modified_questions(self):
        self.survey_question.delete()
        survey_question = SurveyFormFieldFactory(
            page=self.survey, label='Question 02', admin_label='Q 02', field_type='checkboxes',
            skip_logic=self.skip_logic, default_value='c3')
        form_data = json.dumps({
            survey_question.clean_name: [
                'c3',
            ],
        })
        user_submission = UserSubmissionFactory(page=self.survey, user=self.user_01, form_data=form_data)
        user_submission.submit_time = self.current_datetime
        user_submission.save()
        response = self.client.get(f'{self.url}?user_id={self.user_01.id}&export=csv&page_ids={self.survey.id}')

        byte_response = b''
        for stream in response.streaming_content:
            byte_response += stream
        expected_response = \
            f'ID,Name,Submission Date,Field,Value\r\n' \
            f'{user_submission.id},Survey 01,2022-09-01 23:00:00+00:00,User,test\r\n' \
            f'{user_submission.id},Survey 01,2022-09-01 23:00:00+00:00,URL,{self.survey.full_url}\r\n' \
            f'{user_submission.id},Survey 01,2022-09-01 23:00:00+00:00,Q 02,c3\r\n' \
            f'{self.user_submission_02.id},Survey 01,2022-08-31 23:00:00+00:00,User,test\r\n' \
            f'{self.user_submission_02.id},Survey 01,2022-08-31 23:00:00+00:00,URL,{self.survey.full_url}\r\n' \
            f'{self.user_submission_02.id},Survey 01,2022-08-31 23:00:00+00:00,question_01,c2\r\n'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(byte_response.decode(), expected_response)


class PollTest(WebTest):
    def setUp(self):
        root_page = Page.objects.filter(depth=1).first()
        home_page = HomePageFactory(parent=root_page)
        SiteFactory(hostname='testserver', root_page=home_page)
        self.poll_index_page = PollIndexPageFactory(parent=home_page)
        self.user = AdminUserFactory()
        self.client.force_login(self.user)

    def _add_dynamic_field(self, form, name, value):
        field = Hidden(form, tag='input', name=name, value=value, pos=999)
        form.fields[name] = [field]
        form.field_order.append((name, field))

    def test_poll_question_choices_with_surrounding_spaces(self):
        form = self.app.get(
            reverse('wagtailadmin_pages:add', args=('questionnaires', 'poll', self.poll_index_page.id)),
            user=self.user.username
        ).forms[1]
        form['title'] = 'Poll 01'
        form['slug'] = 'poll-01'
        form['poll_form_fields-0-label'] = 'Q1'
        form['poll_form_fields-0-field_type'] = 'checkboxes'
        form['poll_form_fields-0-choices'] = ' c1 | c2 | c3 '
        form['poll_form_fields-0-admin_label'] = 'Q1'
        self._add_dynamic_field(form, 'description-count', '0')
        self._add_dynamic_field(form, 'thank_you_text-count', '0')
        self._add_dynamic_field(form, 'terms_and_conditions-count', '0')

        response = form.submit().follow()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        page = Page.objects.get(path__startswith=self.poll_index_page.path, slug='poll-01').specific
        self.assertEqual(page.get_form_fields().first().choices, 'c1|c2|c3')
