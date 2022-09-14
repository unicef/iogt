from selenium_tests.base import BaseSeleniumTests
from wagtail.core.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import HomePageFactory
from wagtail_factories import SiteFactory
from selenium_tests.pages import LoginPage
from selenium.webdriver.common.by import By

class LoginSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        
        Site.objects.all().delete()
        self.home = HomePageFactory()
        self.site = SiteFactory(
            site_name='IoGT',
            hostname=self.host,
            port=self.port,
            is_default_site=True,
            root_page=self.home
        )
        self.user = AdminUserFactory()
        
    def test_login(self):

        # Tried to test this by clicking the button from the homepage but couldn't get this to work..
        # self.visit_page(self.home)
        # home_page = HomePage(self.selenium)
        # home_page.login_button.click() 

        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        
        login_page = LoginPage(self.selenium) 

        login_page.login_user_name.send_keys(self.user.username)
        login_page.login_password.send_keys('test@123')
        login_page.login_submit.click()

        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn(self.user.username, body_text)
        
