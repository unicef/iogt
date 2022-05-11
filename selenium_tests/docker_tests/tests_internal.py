import time
import socket
from django.test import override_settings, tag
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@override_settings(ALLOWED_HOSTS=['*'])
class SeleniumTest(LiveServerTestCase):
    """
    Provides base test class which connects to the Docker
    container running selenium.
    """
    host = '0.0.0.0'

    
    def setUp(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.selenium = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX
      )

    fixtures = ['basic_fixture.json']

    def login_page_load(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        assert 'Log in' in self.selenium.title

    def test_login(self): 
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))       
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys('tester')
        time.sleep(1)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('tester')
        time.sleep(1)
        submit = self.selenium.find_element_by_xpath("//button[@type='submit']")
        submit.send_keys(Keys.RETURN)
        time.sleep(1)

    def login_result(self):
        assert 'tester' in self.selenium.page_source

    def tearDown(self):
        self.selenium.quit()  # quit vs close?