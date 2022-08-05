import time
from selenium_tests.base import BaseSeleniumTests
from selenium.webdriver.support.ui import Select
from wagtail.core.models import Site
from questionnaires.models import SurveyFormField

from iogt_users.factories import AdminUserFactory
from home.factories import ArticleFactory, HomePageFactory, SectionFactory
from questionnaires.factories import SurveyFactory
from wagtail_factories import SiteFactory

class QuestionnaireInputsSeleniumTests(BaseSeleniumTests):

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
        
