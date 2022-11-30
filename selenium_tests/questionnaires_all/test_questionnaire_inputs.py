import time

from selenium_tests.base import BaseSeleniumTests
from selenium.webdriver.support.ui import Select
from wagtail.core.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory
from questionnaires.factories import SurveyFactory, SurveyFormFieldFactory
from selenium_tests.pages import QuestionnairePage

class QuestionnaireInputsSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)
        self.survey01 = SurveyFactory(parent=self.section01, owner=self.user)

    def test_checkbox(self): 

        self.Q1 = SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,
            choices = "true|false",  
            default_value='',  
            field_type='checkbox', 
        )       

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.select_checkbox()
        survey_page.submit_response()
        
    def test_checkboxes(self):    

        self.Q2 = SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='checkboxes', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.select_checkboxes("B")
        survey_page.submit_response()

    def test_date(self):

        self.Q3 = SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='date', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_date("11111111")
        survey_page.submit_response()

    def test_date_time(self):

        self.Q4 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=3,
            required = True,  
            default_value='',  
            field_type='datetime', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_date_time("11111111", "1111AM")
        survey_page.submit_response()

    def test_dropdown(self):

        self.Q5 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=4,
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='dropdown', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        selection = survey_page.use_dropdown(self.Q5.label, "C")
        self.assertIn("C", selection)
        survey_page.submit_response()

    def test_email(self):

        self.Q6 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=5,
            required = True,  
            default_value='',  
            field_type='email', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_email("tester@gmail.com")
        survey_page.submit_response()

    def test_singleline(self):

        self.Q7 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=6,
            required = True,  
            default_value='',  
            field_type='singleline', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()

    def test_multiline(self):

        self.Q8 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=7,
            required = True,  
            default_value='',  
            field_type='multiline', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("""Testing some multiline text
        Checking that everying
        Looks ok
        when there are multiple lines""")
        survey_page.submit_response()

    def test_number(self):

        self.Q9 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=8,
            required = True,  
            default_value='',  
            field_type='number', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_number("5")
        survey_page.submit_response()

    def test_radio(self):

        self.Q10 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=10,
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='radio', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.select_checkboxes("B")
        survey_page.submit_response()

    def test_url(self):

        self.Q11 = SurveyFormFieldFactory(
            page=self.survey01, 
            sort_order=11,
            required = True,  
            default_value='',  
            field_type='url', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_url("www.google.com")
        survey_page.submit_response()
        
        
