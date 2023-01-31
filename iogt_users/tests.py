from django.test import TestCase
from rest_framework import status
from wagtail.core.models import Site

from home.factories import SiteSettingsFactory, HomePageFactory
from iogt_users.factories import UserFactory, AdminUserFactory, GroupFactory
from wagtail_factories import SiteFactory, PageFactory
from questionnaires.factories import SurveyFactory
from django.contrib.auth.models import Permission


class PostRegistrationRedirectTests(TestCase):
    def setUp(self):
        self.user = UserFactory(has_filled_registration_survey=False)

        root_page = PageFactory(parent=None)
        self.home_page = HomePageFactory(parent=root_page)
        self.site = SiteFactory(hostname='testserver', port=80, root_page=self.home_page)

        self.registration_survey = SurveyFactory(parent=self.home_page)
        self.site_settings = SiteSettingsFactory.create(
            registration_survey=self.registration_survey, site=self.site)

    def test_user_locked_out_without_filling_registration_survey_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.registration_survey.url)

    def test_anonymous_user_can_browse_public_urls(self):
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_without_filling_registration_survey_form(self):
        admin_user = AdminUserFactory(has_filled_registration_survey=False)

        self.client.force_login(admin_user)
        response = self.client.get(self.home_page.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_with_admin_access_do_not_need_to_fill_registration_survey_form(self):
        admin_access_permission = Permission.objects.get(codename='access_admin')
        group = GroupFactory()
        group.permissions.add(admin_access_permission)

        self.user.groups.add(group)
        self.client.force_login(self.user)
        response = self.client.get(self.home_page.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
