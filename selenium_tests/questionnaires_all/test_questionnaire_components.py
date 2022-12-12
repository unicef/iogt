import time

from selenium_tests.base import BaseSeleniumTests
from selenium.webdriver.support.ui import Select
from wagtail.core.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory
from questionnaires.factories import SurveyFactory, SurveyFormFieldFactory
from selenium_tests.pages import QuestionnairePage, QuestionnaireResultsPage

class QuestionnaireInputsSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)
        self.survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user, 
            direct_display=True, 
            description="[{\"type\": \"paragraph\", \"value\": \"<p>This is a simple survey description</p>\"}]",
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )
        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='singleline', 
        )

    def test_direct_display(self):
        self.visit_page(self.section01)
        #We are looking at a section here, but use the Questionnaire page as we want to test the functionality of the direct display questionnaire
        survey_page = QuestionnairePage(self.selenium)
        self.assertIn("This is a simple survey description", survey_page.get_content_text())
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_title(self):
        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        self.assertIn(self.survey01.title, survey_page.title)

    def test_description(self):
        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        self.assertIn("This is a simple survey description", survey_page.get_content_text())

    def test_basic_result(self):
        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())



        
        
        
