import time

from selenium_tests.base import BaseSeleniumTests
from selenium.webdriver.support.ui import Select
from wagtail.core.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory
from questionnaires.factories import QuizFactory, QuizFormFieldFactory
from selenium_tests.pages import QuestionnairePage, QuestionnaireResultsPage

class QuizSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)
        

    def test_correct_quiz(self):
        quiz01 = QuizFactory(
            parent=self.section01, 
            owner=self.user,
            )
        QuizFormFieldFactory(
            page=quiz01, 
            required = True,
            choices = "A|B|C",  
            default_value='',
            correct_answer = "B",  
            field_type='checkboxes', 
        )

        self.visit_page(quiz01)
        quiz_page = QuestionnairePage(self.selenium)
        quiz_page.select_checkboxes("B")
        quiz_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        quiz_result = results_page.get_quiz_results_text()
        self.assertIn("1 Correct", quiz_result)

    def test_incorrect_quiz(self):
        quiz01 = QuizFactory(
            parent=self.section01, 
            owner=self.user,
            )
        QuizFormFieldFactory(
            page=quiz01, 
            required = True,
            choices = "A|B|C",  
            default_value='',
            correct_answer = "B",  
            field_type='checkboxes', 
        )

        self.visit_page(quiz01)
        quiz_page = QuestionnairePage(self.selenium)
        quiz_page.select_checkboxes("A")
        quiz_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        quiz_result = results_page.get_quiz_results_text()
        self.assertIn("1 Incorrect", quiz_result)
        
        

        
        
