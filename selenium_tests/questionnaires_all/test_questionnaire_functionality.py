import time
import json

from selenium_tests.base import BaseSeleniumTests
from selenium.webdriver.support.ui import Select
from wagtail.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory
from questionnaires.factories import SurveyFactory, SurveyFormFieldFactory
from selenium_tests.pages import QuestionnairePage, QuestionnaireResultsPage, LoginPage

class QuestionnaireFunctionalitySeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)
        

    def test_single_submission(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            allow_multiple_submissions = False
            )
        SurveyFormFieldFactory(
            page=survey01, 
            required = True,  
            default_value='',  
            field_type='singleline', 
        )
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        revisit_page = self.visit_page(survey01)
        self.assertIn("You have already completed this survey.", revisit_page.get_content_text())

    def test_multiple_submission(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            allow_multiple_submissions = True,
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )
        SurveyFormFieldFactory(
            page=survey01, 
            required = True,  
            default_value='',  
            field_type='singleline', 
        )
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_required_optional_submission(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            allow_multiple_submissions = True,
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )
        SurveyFormFieldFactory(
            page=survey01, 
            required = False,  
            default_value='',  
            field_type='singleline', 
        )
        SurveyFormFieldFactory(
            page=survey01, 
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='checkboxes', 
        )
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        self.assertIn("OPTIONAL", survey_page.get_content_text())
        survey_page.submit_response()
        self.assertIn("This field is required.", survey_page.get_content_text())
        survey_page.select_checkboxes("B")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_multiple_page_survey(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            multi_step = True,
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )
        SurveyFormFieldFactory(
            page=survey01, 
            required = False,  
            default_value='',  
            field_type='singleline',
            page_break = True 
        )
        SurveyFormFieldFactory(
            page=survey01, 
            required = False,
            choices = "A|B|C",  
            default_value='',  
            field_type='checkboxes', 
        )
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.submit_response()
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_survey_require_login(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            allow_anonymous_submissions = False,
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )
        SurveyFormFieldFactory(
            page=survey01, 
            required = True,  
            default_value='',  
            field_type='singleline',
            page_break = True 
        )
        
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.login_button_submit()
        login_page = LoginPage(self.selenium)
        login_page.login_user(self.user)
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_survey_back(self):
        survey01 = SurveyFactory(parent=self.section01, owner=self.user)
        SurveyFormFieldFactory(
            page=survey01, 
            required = True,  
            default_value='',  
            field_type='singleline',
            page_break = True 
        )
        
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        results_page.go_back()
        current_page = QuestionnairePage(self.selenium)
        self.assertIn(survey01.title, current_page.title)

    def test_skip_question(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            allow_multiple_submissions = True,
            multi_step = True,
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )

        skip_logic = [
            {
                'type': 'skip_logic',
                'value': {
                    'choice': 'A',
                    'skip_logic': 'next'
                    },
            }, 
            {
                'type': 'skip_logic', 
                'value': {
                    'choice': 'B', 
                    'skip_logic': 'question', 
                    'question': 3
                    },
            }, 
            {
                'type': 'skip_logic', 
                'value': {
                    'choice': 'C', 
                    'skip_logic': 'next', 
                    }, 
            }
        ]
        json_skip_logic = json.dumps(skip_logic)

        SurveyFormFieldFactory(
            page=survey01,
            sort_order= 0,
            required=True,
            choices= "A|B|C",
            clean_name= "question_1",
            label= "XXXX",
            field_type= "radio",
            admin_label= "q1",
            skip_logic= json_skip_logic,
            default_value= "",
            page_break=True
        )

        SurveyFormFieldFactory(
            page=survey01,
            sort_order= 1,
            required=False,
            choices= "",
            help_text= "",
            clean_name = "question_2",
            label= "YYYY",
            field_type= "singleline",
            admin_label= "q2",
            skip_logic= "[]",
            default_value= "",
            page_break=True
        )

        SurveyFormFieldFactory(
            page=survey01,
            sort_order= 2,
            required=False,
            choices= "",
            help_text= "",
            clean_name= "question_3",
            label= "ZZZZ",
            field_type= "singleline",
            admin_label= "q3",
            skip_logic= "[]",
            default_value= "",
            page_break=True
        )
        
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.select_checkboxes("B")
        survey_page.submit_response()
        current_question = QuestionnairePage(self.selenium)
        self.assertIn("ZZZZ", current_question.get_content_text())
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())

    def test_skip_end_survey(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            allow_multiple_submissions = True,
            multi_step = True,
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]"
            )
        
        skip_logic = [
            {
                'type': 'skip_logic',
                'value': {
                    'choice': 'A',
                    'skip_logic': 'next',
                    },
            }, 
            {
                'type': 'skip_logic', 
                'value': {
                    'choice': 'C', 
                    'skip_logic': 'end', 
                    }, 
            }
        ]
        json_skip_logic = json.dumps(skip_logic)

        SurveyFormFieldFactory(
            page=survey01,
            sort_order= 0,
            required=True,
            choices= "A|C",
            clean_name= "question_1",
            label= "XXXX",
            field_type= "radio",
            admin_label= "q1",
            skip_logic= json_skip_logic,
            default_value= "",
            page_break=True
        )

        SurveyFormFieldFactory(
            page=survey01,
            sort_order= 1,
            required=False,
            choices= "",
            help_text= "",
            clean_name = "question_2",
            label= "YYYY",
            field_type= "singleline",
            admin_label= "q2",
            skip_logic= "[]",
            default_value= "",
            page_break=True
        )
        
        self.visit_page(survey01)
        survey_page = QuestionnairePage(self.selenium)
        survey_page.select_checkboxes("C")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())