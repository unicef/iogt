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


class QuestionnaireSubmissionsAPIViewTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.group = GroupFactory(name='questionnaires')
        self.user.groups.add(self.group)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = 'v2_questionnaire_submissions'

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
        self.assertEqual(response.data['results'][0]['submission'][0]['admin_label'], poll_question.admin_label)
        self.assertEqual(response.data['results'][0]['submission'][0]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][0]['submission'][0]['user_answer'], ['c1'])
        self.assertEqual(response.data['results'][1]['id'], user_submission_02.id)
        self.assertEqual(response.data['results'][1]['user'], user_02.username)
        self.assertIsNotNone(response.data['results'][1]['submit_time'])
        self.assertEqual(response.data['results'][1]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][1]['submission'][0]['admin_label'], poll_question.admin_label)
        self.assertEqual(response.data['results'][1]['submission'][0]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][1]['submission'][0]['user_answer'], ['c2', 'c3'])
        self.assertEqual(response.data['results'][2]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][2]['id'], user_submission_03.id)
        self.assertEqual(response.data['results'][2]['user'], user_03.username)
        self.assertIsNotNone(response.data['results'][2]['submit_time'])
        self.assertEqual(response.data['results'][2]['page_url'], poll.full_url)
        self.assertEqual(response.data['results'][2]['submission'][0]['admin_label'], poll_question.admin_label)
        self.assertEqual(response.data['results'][2]['submission'][0]['clean_name'], poll_question.clean_name)
        self.assertEqual(response.data['results'][2]['submission'][0]['user_answer'], ['c3'])
