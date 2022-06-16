import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from home.factories import SurveyFactory, SectionFactory
from home.models import HomePage
from iogt_users.factories import AdminUserFactory
from comments.models import CommentStatus
from django.conf import settings
from home.models import HomePage

class MySeleniumTests(LiveServerTestCase):

    host = 'django'
    port = 9000

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        # options.add_argument("--headless")
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
        self.user = AdminUserFactory()
        self.home_page = HomePage.objects.first()
        self.section01 = SectionFactory.build(
            owner=self.user,            
        )
        self.survey01 = SurveyFactory.build(
            owner=self.user,            
        )
        self.home_page.add_child(instance=self.section01)
        self.section01.add_child(instance=self.survey01)

    def test_survey(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        time.sleep(2)
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys(self.user.username)
        time.sleep(2)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test@123')
        time.sleep(2)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        body_text = self.selenium.find_element_by_tag_name('body').text
        assert self.user.username in body_text        

        self.selenium.get('%s%s' % (self.live_server_url, '/section0/survey0/'))
        time.sleep(2)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(100)
     
        
        
        
