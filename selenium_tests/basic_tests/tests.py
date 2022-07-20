from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from wagtail.core.models import Site

from iogt_users.factories import AdminUserFactory
from home.factories import ArticleFactory, HomePageFactory
from wagtail_factories import SiteFactory


class MySeleniumTests(LiveServerTestCase):

    host = 'django'
    port = 9000

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options
        )
        cls.selenium.implicitly_wait(5)
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    def setUp(self):
        Site.objects.all().delete()
        self.site = SiteFactory(site_name='IoGT', port=8000, is_default_site=True)
        self.user = AdminUserFactory()
        self.home_page = HomePageFactory(parent=self.site.root_page, owner=self.user)
        self.article01 = ArticleFactory(parent=self.home_page, owner=self.user)

    def test_article_comment(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys(self.user.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test@123')
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        body_text = self.selenium.find_element_by_tag_name('body').text
        assert self.user.username in body_text
        self.selenium.get('%s%s' % (self.live_server_url, self.article01.url))
        comment_input = self.selenium.find_element_by_name("comment")
        comment_input.send_keys('Test comment')
        self.selenium.find_element_by_xpath('//input[@value="Leave comment"]').send_keys(Keys.RETURN)
