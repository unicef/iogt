from django.test import TestCase
from rest_framework import status
from wagtail.core.models import Site

from comments.models import CommentStatus
from home.factories import ArticleFactory, SurveyFactory, SiteSettingsFactory
from home.models import HomePage
from iogt_users.factories import UserFactory


class PostRegistrationRedirectTests(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory(has_filled_registration_survey=False)
        self.admin_user = UserFactory()

        self.home_page = HomePage.objects.first()
        self.public_article = ArticleFactory.build(owner=self.admin_user, commenting_status=CommentStatus.OPEN)
        self.home_page.add_child(instance=self.public_article)

        self.registration_survey = SurveyFactory.build()
        self.home_page.add_child(instance=self.registration_survey)

        self.site = Site.objects.filter(is_default_site=True).first()
        self.site_settings = SiteSettingsFactory.create(registration_survey=self.registration_survey,
                                                        site_id=self.site.id)

    def test_user_locked_out_without_filling_registration_survey_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response.url, self.registration_survey.url)

    def test_anonymous_user_can_browse_public_urls(self):
        response = self.client.get(self.home_page.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
