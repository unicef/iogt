import time
import urllib
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class HostTest(LiveServerTestCase):

    def testhomepage(self):

        driver = webdriver.Chrome()
        driver.get(self.live_server_url)
        time.sleep(10)
        assert 'Home' in driver.title
        driver.quit()


