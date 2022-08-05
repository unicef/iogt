from selenium_tests.base import BaseSeleniumTests

from wagtail.core.models import Site

from iogt_users.factories import AdminUserFactory
from home.factories import HomePageFactory
from wagtail_factories import SiteFactory

class LoginSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.user = AdminUserFactory()
        self.home_page = HomePageFactory(parent=self.site.root_page, owner=self.user)
        
    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys(self.user.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test@123')
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        body_text = self.selenium.find_element_by_tag_name('body').text
        assert self.user.username in body_text
        
