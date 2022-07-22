import datetime
import io
import json
from datetime import timedelta

import pytz
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook
from rest_framework import status
from rest_framework.test import APIClient
from wagtail.core.models import Site
from wagtail_factories import SiteFactory

from home.factories import HomePageFactory
from iogt_users.factories import (
    UserFactory,
    GroupFactory,
    GroupPagePermissionFactory,
)
from questionnaires.factories import (
    PollFactory,
    SurveyFactory,
    QuizFactory,
    PollFormFieldFactory,
    SurveyFormFieldFactory,
    QuizFormFieldFactory,
    UserSubmissionFactory
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

    def test_questionnaires_list_published_at_filter(self):
        current_datetime = timezone.now()
        poll_01 = PollFactory(parent=self.home_page, title='Poll 01', last_published_at=current_datetime)
        poll_02 = PollFactory(parent=self.home_page, title='Poll 02', last_published_at=current_datetime - timedelta(days=1))
        poll_03 = PollFactory(parent=self.home_page, title='Poll 03', last_published_at=current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=poll_01)
        GroupPagePermissionFactory(group=self.group, page=poll_02)
        GroupPagePermissionFactory(group=self.group, page=poll_03)

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
        self.assertEqual(response.data['results'][0]['title'], survey_01.title)
        self.assertEqual(response.data['results'][1]['title'], survey_02.title)
        self.assertEqual(response.data['results'][2]['title'], survey_03.title)

        response = self.client.get(f'{self.url}?page=3&page_size=3')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 9)
        self.assertIsNone(response.data['next'])
        self.assertEqual(response.data['previous'], 'http://testserver/questionnaires/list/?page=2&page_size=3')
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
        self.assertIsNotNone(response.data['published_at'])
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
        self.assertEqual(response.data['questions'][0]['default_value'], poll_question.default_value)
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
        self.assertIsNotNone(response.data['published_at'])
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
        self.assertEqual(response.data['questions'][0]['default_value'], survey_question.default_value)
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
        self.assertIsNotNone(response.data['published_at'])
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
        self.assertEqual(response.data['questions'][0]['default_value'], quiz_question.default_value)
        self.assertEqual(response.data['questions'][0]['correct_answer'], quiz_question.correct_answer)
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
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c1'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][1]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][poll_question.clean_name], ['c2', 'c3'])
        self.assertEqual(response.data['results'][2]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][2]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][2]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][2]['submit_time'])
        self.assertEqual(response.data['results'][2]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][2]['submission'][poll_question.clean_name], ['c3'])

    def test_questionnaire_submission_list_submit_at_filter(self):
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
            f"{reverse(self.url, kwargs={'pk': poll.id})}?submit_at_start={(current_datetime - timedelta(days=1)).date()}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_01.id)
        self.assertEqual(response.data['results'][0]['user'], user_01.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c1'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][1]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][poll_question.clean_name], ['c2', 'c3'])

        response = self.client.get(
            f"{reverse(self.url, kwargs={'pk': poll.id})}?submit_at_end={(current_datetime - timedelta(days=1)).date()}")

        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][0]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c2', 'c3'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][poll_question.clean_name], ['c3'])

    def test_questionnaire_submission_list_user_ids_filter(self):
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

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?user_ids={user_01.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_01.id)
        self.assertEqual(response.data['results'][0]['user'], user_01.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c1'])

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?user_ids={user_02.id},{user_03.id}")

        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][0]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c2', 'c3'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][1]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][poll_question.clean_name], ['c3'])

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
            response.data['next'], f'http://testserver/questionnaires/{poll.id}/submissions/?page=2&page_size=1')
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'][0]['id'], user_submission_01.id)
        self.assertEqual(response.data['results'][0]['user'], user_01.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c1'])

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?page=2&page_size=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(
            response.data['next'], f'http://testserver/questionnaires/{poll.id}/submissions/?page=3&page_size=1')
        self.assertEqual(
            response.data['previous'], f'http://testserver/questionnaires/{poll.id}/submissions/?page_size=1')
        self.assertEqual(response.data['results'][0]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][0]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c2', 'c3'])

        response = self.client.get(f"{reverse(self.url, kwargs={'pk': poll.id})}?page=3&page_size=1")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertIsNone(response.data['next'])
        self.assertEqual(
            response.data['previous'], f'http://testserver/questionnaires/{poll.id}/submissions/?page=2&page_size=1')
        self.assertEqual(response.data['results'][0]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][0]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][0]['submit_time'])
        self.assertEqual(response.data['results'][0]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][0]['submission'][poll_question.clean_name], ['c3'])

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


class QuestionnairesTests(TestCase):
    def setUp(self):
        self.group = GroupFactory(name='questionnaires')
        self.admin_access_permission = Permission.objects.get(codename='access_admin')
        self.group.permissions.add(self.admin_access_permission)
        self.staff_user = UserFactory()
        self.staff_user.groups.add(self.group)
        self.client.force_login(self.staff_user)
        self.url = reverse('questionnaires')

        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

    def test_questionnaires_list_pages(self):
        current_datetime = timezone.now()

        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime)
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        survey = SurveyFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=1))
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

        quiz = QuizFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=quiz)
        quiz_question = QuizFormFieldFactory(
            page=quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)

        form_data_02 = json.dumps({
            survey_question.clean_name: [
                'c2',
            ],
        })
        UserSubmissionFactory(page=survey, user=user_01, form_data=form_data_02)

        user_02 = UserFactory()
        form_data_03 = json.dumps({
            quiz_question.clean_name: [
                'c3',
            ],
        })
        UserSubmissionFactory(page=quiz, user=user_02, form_data=form_data_03)

        response = self.client.get(f'{self.url}?user_id={user_01.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 2)
        self.assertEqual(response.context['form_pages'][0].title, poll.title)
        self.assertEqual(response.context['form_pages'][1].title, survey.title)

        response = self.client.get(f'{self.url}?user_id={user_02.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 1)
        self.assertEqual(response.context['form_pages'][0].title, quiz.title)

    def test_questionnaires_list_pages_date_range_filter(self):
        current_datetime = timezone.now()

        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime)
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        survey = SurveyFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=1))
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

        quiz = QuizFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=quiz)
        quiz_question = QuizFormFieldFactory(
            page=quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        form_data_02 = json.dumps({
            survey_question.clean_name: [
                'c2',
            ],
        })
        user_submission_02 = UserSubmissionFactory(page=survey, user=user_01, form_data=form_data_02)
        user_submission_02.submit_time = current_datetime - timedelta(days=1)
        user_submission_02.save()

        form_data_03 = json.dumps({
            quiz_question.clean_name: [
                'c3',
            ],
        })
        user_submission_03 = UserSubmissionFactory(page=quiz, user=user_01, form_data=form_data_03)
        user_submission_03.submit_time = current_datetime - timedelta(days=2)
        user_submission_03.save()

        response = self.client.get(f'{self.url}?user_id={user_01.id}&date_from={(current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 2)
        self.assertEqual(response.context['form_pages'][0].title, poll.title)
        self.assertEqual(response.context['form_pages'][1].title, survey.title)

        response = self.client.get(f'{self.url}?user_id={user_01.id}&date_to={(current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 2)
        self.assertEqual(response.context['form_pages'][0].title, survey.title)
        self.assertEqual(response.context['form_pages'][1].title, quiz.title)

        response = self.client.get(f'{self.url}?user_id={user_01.id}&date_from={(current_datetime - timedelta(days=1)).date()}&date_to={(current_datetime - timedelta(days=1)).date()}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 1)
        self.assertEqual(response.context['form_pages'][0].title, survey.title)

    def test_user_submissions_csv_export(self):
        current_datetime = timezone.now()

        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime)
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        survey = SurveyFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=1))
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

        quiz = QuizFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=quiz)
        quiz_question = QuizFormFieldFactory(
            page=quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        form_data_02 = json.dumps({
            survey_question.clean_name: [
                'c2',
            ],
        })
        user_submission_02 = UserSubmissionFactory(page=survey, user=user_01, form_data=form_data_02)
        user_submission_02.submit_time = current_datetime - timedelta(days=1)
        user_submission_02.save()

        user_02 = UserFactory()
        form_data_03 = json.dumps({
            quiz_question.clean_name: [
                'c3',
            ],
        })
        user_submission_03 = UserSubmissionFactory(page=quiz, user=user_02, form_data=form_data_03)
        user_submission_03.submit_time = current_datetime - timedelta(days=2)
        user_submission_03.save()

        response = self.client.get(f'{self.url}?user_id={user_01.id}&export=csv')

        byte_response = b''
        for stream in response.streaming_content:
            byte_response += stream
        expected_response = \
            f'ID,Name,Submission Date,Field,Value\r\n' \
            f'{user_submission_01.id},{poll.title},{user_submission_01.submit_time},User,{user_01.username}\r\n' \
            f'{user_submission_01.id},{poll.title},{user_submission_01.submit_time},URL,{poll.full_url}\r\n' \
            f'{user_submission_01.id},{poll.title},{user_submission_01.submit_time},{poll_question.clean_name},c1\r\n' \
            f'{user_submission_02.id},{survey.title},{user_submission_02.submit_time},User,{user_01.username}\r\n' \
            f'{user_submission_02.id},{survey.title},{user_submission_02.submit_time},URL,{survey.full_url}\r\n' \
            f'{user_submission_02.id},{survey.title},{user_submission_02.submit_time},{survey_question.clean_name},c2\r\n'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(byte_response.decode(), expected_response)

    def test_user_submissions_xlsx_export(self):
        current_datetime = timezone.now().replace(microsecond=0)

        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime)
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        survey = SurveyFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=1))
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

        quiz = QuizFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=2))
        GroupPagePermissionFactory(group=self.group, page=quiz)
        quiz_question = QuizFormFieldFactory(
            page=quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        user_submission_01 = UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)
        user_submission_01.submit_time = current_datetime
        user_submission_01.save()

        form_data_02 = json.dumps({
            survey_question.clean_name: [
                'c2',
            ],
        })
        user_submission_02 = UserSubmissionFactory(page=survey, user=user_01, form_data=form_data_02)
        user_submission_02.submit_time = current_datetime - timedelta(days=1)
        user_submission_02.save()

        user_02 = UserFactory()
        form_data_03 = json.dumps({
            quiz_question.clean_name: [
                'c3',
            ],
        })
        user_submission_03 = UserSubmissionFactory(page=quiz, user=user_02, form_data=form_data_03)
        user_submission_03.submit_time = current_datetime - timedelta(days=2)
        user_submission_03.save()

        response = self.client.get(f'{self.url}?user_id={user_01.id}&export=xlsx')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        sheet = load_workbook(io.BytesIO(response.content)).active
        expected_response = {
            'A': {
                1: 'ID',
                2: f'{user_submission_01.id}',
                3: f'{user_submission_01.id}',
                4: f'{user_submission_01.id}',
                5: f'{user_submission_02.id}',
                6: f'{user_submission_02.id}',
                7: f'{user_submission_02.id}',
            },
            'B': {
                1: 'Name',
                2: poll.title,
                3: poll.title,
                4: poll.title,
                5: survey.title,
                6: survey.title,
                7: survey.title,
            },
            'C': {
                1: 'Submission Date',
                2: user_submission_01.submit_time,
                3: user_submission_01.submit_time,
                4: user_submission_01.submit_time,
                5: user_submission_02.submit_time,
                6: user_submission_02.submit_time,
                7: user_submission_02.submit_time,
            },
            'D': {
                1: 'Field',
                2: 'User',
                3: 'URL',
                4: poll_question.clean_name,
                5: 'User',
                6: 'URL',
                7: survey_question.clean_name,
            },
            'E': {
                1: 'Value',
                2: user_01.username,
                3: poll.full_url,
                4: 'c1',
                5: user_01.username,
                6: survey.full_url,
                7: 'c2',
            },
        }

        for row in [1, 2, 3, 4, 5, 6, 7]:
            for column in ['A', 'B', 'C', 'D', 'E']:
                value = sheet[f'{column}{row}'].value
                if isinstance(value, datetime.datetime):
                    value = value.replace(tzinfo=pytz.UTC)
                self.assertEqual(value, expected_response[column][row])

    def test_questionnaires_list_pages_permission(self):
        current_datetime = timezone.now()

        poll = PollFactory(parent=self.home_page, last_published_at=current_datetime)
        GroupPagePermissionFactory(group=self.group, page=poll)
        poll_question = PollFormFieldFactory(page=poll, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')

        survey = SurveyFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=1))
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

        quiz = QuizFactory(parent=self.home_page, last_published_at=current_datetime - timedelta(days=2))
        quiz_question = QuizFormFieldFactory(
            page=quiz, field_type='checkboxes', choices='c1|c2|c3', default_value='c2', correct_answer='c3')

        user_01 = UserFactory()
        form_data_01 = json.dumps({
            poll_question.clean_name: [
                'c1',
            ],
        })
        UserSubmissionFactory(page=poll, user=user_01, form_data=form_data_01)

        form_data_02 = json.dumps({
            survey_question.clean_name: [
                'c2',
            ],
        })
        UserSubmissionFactory(page=survey, user=user_01, form_data=form_data_02)

        form_data_03 = json.dumps({
            quiz_question.clean_name: [
                'c3',
            ],
        })
        UserSubmissionFactory(page=quiz, user=user_01, form_data=form_data_03)

        response = self.client.get(f'{self.url}?user_id={user_01.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['form_pages'].count(), 2)
        self.assertEqual(response.context['form_pages'][0].title, poll.title)
        self.assertEqual(response.context['form_pages'][1].title, survey.title)
