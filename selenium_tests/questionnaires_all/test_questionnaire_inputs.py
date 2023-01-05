from selenium_tests.base import BaseSeleniumTests
from selenium.webdriver.support.ui import Select
from wagtail.core.models import Site
from questionnaires.models import SurveyFormField
from iogt_users.factories import AdminUserFactory
from home.factories import ArticleFactory, SectionFactory
from questionnaires.factories import SurveyFactory

class QuestionnaireInputsSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)
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
        self.assertIn('blah3', select.first_selected_option.text)
        
