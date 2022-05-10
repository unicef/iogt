import time
import socket

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class MySeleniumTests(StaticLiveServerTestCase):

     # We need the following to get Selenium to communicate with our
    # Live Server, which needs to work for us to be able to
# authenticate users in the test.
    host = '172.18.0.6'  # TODO: bring in argument properly
    port = 5000   # Would yield: self.live_server_url = "http://172.17.0.2:5000"
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.host = 'web'
        cls.selenium = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
      )   
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get(self.live_server_url)
        time.sleep(5)  # simulate long running test
        
        