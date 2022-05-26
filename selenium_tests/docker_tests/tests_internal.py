import time

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumTest(LiveServerTestCase):
    
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        self.chrome = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options
      )      

        self.firefox = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX
      )
       
    def test_homepage(self):
        browser = self.chrome
        browser.get(self.live_server_url)
        time.sleep(4)
        

    def tearDown(self):
        self.chrome.quit()
        self.firefox.quit()  # quit vs close?