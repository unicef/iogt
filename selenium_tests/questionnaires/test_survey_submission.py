import time
from selenium_tests.base import BaseSeleniumTests
from wagtail.core.models import Site

from iogt_users.factories import AdminUserFactory
from home.factories import HomePageFactory
from questionnaires.factories import SurveyFactory
from wagtail_factories import SiteFactory


class SurveySeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.user = AdminUserFactory()
        self.home_page = HomePageFactory(parent=self.site.root_page, owner=self.user)
        self.survey01 = SurveyFactory(parent=self.home_page, owner=self.user)

    def test_submit_survey_and_get_back(self):
        self.selenium.get('%s%s' % (self.live_server_url, self.survey01.url))
       

        
        
