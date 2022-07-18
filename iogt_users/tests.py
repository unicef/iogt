from django.test import TestCase
from rest_framework import status
from wagtail.core.models import Site

from home.factories import SiteSettingsFactory, HomePageFactory
from iogt_users.factories import UserFactory
from wagtail_factories import SiteFactory

from questionnaires.factories import SurveyFactory


class PostRegistrationRedirectTests(TestCase):
    def setUp(self):
        self.user = UserFactory(has_filled_registration_survey=False)
        self.admin_user = UserFactory()

        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.home_page = HomePageFactory(parent=self.site.root_page)

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
