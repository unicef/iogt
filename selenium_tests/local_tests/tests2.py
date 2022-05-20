import time
from django.test import LiveServerTestCase
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys



class MySeleniumTests(LiveServerTestCase):
    
    fixtures = ['basic_fixture.json']

    """
    BaseCleass for my selenium test cases
    """

    @classmethod
    def setUpClass(cls):  
        cls.selenium = webdriver.Chrome()

        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

class LoginTest(MySeleniumTests):

    def test_login_page_load(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        time.sleep(10)
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

    def test_login_result(self):
        assert 'tester' in self.selenium.page_source


    