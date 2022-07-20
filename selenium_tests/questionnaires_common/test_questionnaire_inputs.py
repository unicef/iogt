import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from wagtail.core.models import Site
from questionnaires.models import SurveyFormField

from iogt_users.factories import AdminUserFactory
from home.factories import ArticleFactory, HomePageFactory, SurveyFactory, SectionFactory
from wagtail_factories import SiteFactory


class MySeleniumTests(LiveServerTestCase):

    fixtures = ['selenium_tests/locales.json']    

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
        self.section01 = SectionFactory(parent=self.home_page, owner=self.user)
        self.article01 = ArticleFactory(parent=self.section01, owner=self.user)
        self.survey01 = SurveyFactory(parent=self.section01, owner=self.user)

        SurveyFormField.objects.create(
            page=self.survey01, 
            sort_order=0,
            required = True,
            choices = "A|B|C", 
            label='Question 1', 
            default_value='',  
            field_type='checkboxes',
            admin_label='Q1',            
        )

        SurveyFormField.objects.create(
            page=self.survey01, 
            sort_order=1,
            required = True,
            choices = "blah1|blah2|blah3", 
            label='Question 2', 
            default_value='',  
            field_type='dropdown',
            admin_label='Q2',            
        )
        
    
    def test_checkboxes(self):
        self.selenium.get('%s%s' % (self.live_server_url, self.survey01.url))
        self.selenium.find_element_by_xpath('//input[@value="A"]').click()
        
    def test_dropdown(self):  
        self.selenium.get('%s%s' % (self.live_server_url, self.survey01.url))  
        select = Select(self.selenium.find_element_by_name("question_2"))
        select.select_by_visible_text("blah3")
        print(select.first_selected_option)
        assert 'blah3' in select.first_selected_option.text
        
