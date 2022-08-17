from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class BaseSeleniumTests(LiveServerTestCase):

    fixtures = ['selenium_tests/locales.json']    

    host = 'django'
    port = 9000

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        #options.add_argument("--window-size=1920,1080")
        #options.add_argument("--start-maximized")
        #options.add_argument("--headless")
        cls.selenium = webdriver.Remote(
            command_executor='http://selenium-hub:4444/wd/hub',
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options
        )
        cls.selenium.implicitly_wait(5)
        super(BaseSeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(BaseSeleniumTests, cls).tearDownClass()

    def visit(self, uri):
        url = '%s%s' % (self.live_server_url, uri)
        self.selenium.get(url)
