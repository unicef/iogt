import time

from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class SeleniumTest(TestCase):

    
    def setUp(self):
        self.chrome = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME
      )      

        self.firefox = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.FIREFOX
      )
       
    def test_hackernews_search_for_testdrivenio(self):
        browser = self.chrome
        browser.get('https://news.ycombinator.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys('testdriven.io')
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # simulate long running test
        self.assertIn('testdriven.io', browser.page_source)

    def test_hackernews_search_for_selenium(self):
        browser = self.chrome
        browser.get('https://news.ycombinator.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys('selenium')
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # simulate long running test
        self.assertIn('selenium', browser.page_source)

    def test_hackernews_search_for_testdriven(self):
        browser = self.firefox
        browser.get('https://news.ycombinator.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys('testdriven')
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # simulate long running test
        self.assertIn('testdriven', browser.page_source)

    def test_hackernews_search_with_no_results(self):
        browser = self.firefox
        browser.get('https://news.ycombinator.com')
        search_box = browser.find_element_by_name('q')
        search_box.send_keys('?*^^%')
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)  # simulate long running test
        self.assertNotIn('<em>', browser.page_source)

    def tearDown(self):
        self.chrome.quit()
        self.firefox.quit()  # quit vs close?


        
        

    

        


    




            