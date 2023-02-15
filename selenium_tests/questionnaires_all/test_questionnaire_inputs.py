import json

from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from selenium_tests.base import BaseSeleniumTests
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
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )
        self.visit_login_page().login_user(self.user)

    def test_checkbox(self): 

        SurveyFormFieldFactory(
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
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())
        
    def test_checkboxes(self):    

        SurveyFormFieldFactory(
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
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_date(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='date', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_date("11111111")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_date_time(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='datetime', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_date_time("12122000", "1111AM")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        results_page_content = results_page.get_content_text()
        self.assertIn("Thankyou for completing the survey", results_page_content)

    def test_dropdown(self):

        question = SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='dropdown', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        selection = survey_page.use_dropdown(question.label, "C")
        self.assertIn("C", selection)
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_email(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='email', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_email("tester@gmail.com")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_singleline(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='singleline', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_multiline(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='multiline', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_multiline_text("""Testing some multiline text
        Checking that everying
        Looks ok
        when there are multiple lines""")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_number(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='number', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_number("5")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_radio(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='radio', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.select_checkboxes("B")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_url(self):

        SurveyFormFieldFactory(
            page=self.survey01, 
            required = True,  
            default_value='',  
            field_type='url', 
        )

        self.visit_page(self.survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_url("https://www.google.com/")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())
        
    def test_skip_logic_validation_errors_on_admin_panel(self):
        skip_logic = json.dumps(
            [
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "true",
                        "skip_logic": "next",
                        "question": None
                    }
                },
                {
                    "type": "skip_logic",
                    "value": {
                        "choice": "false",
                        "skip_logic": "next",
                        "question": None
                    }
                }
            ]
        )

        SurveyFormFieldFactory(label='Q1', page=self.survey01, required=True, field_type='checkbox', skip_logic=skip_logic)
        SurveyFormFieldFactory(label='Q2', page=self.survey01, required=True, field_type='checkbox', skip_logic=skip_logic)
        SurveyFormFieldFactory(label='Q3', page=self.survey01, required=True, field_type='checkbox', skip_logic=skip_logic)

        self.visit_url(reverse('wagtailadmin_pages:edit', args=(self.survey01.id,)))

        select_skip_logic = Select(self.selenium.find_element(By.ID, "survey_form_fields-0-skip_logic-0-value-skip_logic"))
        select_skip_logic.select_by_value("question")
        select_question = Select(self.selenium.find_element(By.ID, "survey_form_fields-0-skip_logic-0-value-question_1"))
        select_question.select_by_value("3")
        self.selenium.find_elements(By.CSS_SELECTOR, "button[type='submit']")[1].click()

        self.assertIn("Skip to question Q3 with in-between required questions isn't allowed.", self.selenium.page_source)
