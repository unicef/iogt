import time

from selenium_tests.base import BaseSeleniumTests
from selenium.webdriver.support.ui import Select
from wagtail.core.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory
from questionnaires.factories import PollFactory, PollFormFieldFactory
from selenium_tests.pages import QuestionnairePage, QuestionnaireResultsPage

class PollSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)
        

    def test_result_totals(self):
        poll01 = PollFactory(
            parent=self.section01, 
            owner=self.user,
            result_as_percentage = False
            )
        PollFormFieldFactory(
            page=poll01, 
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='checkboxes', 
        )

        self.visit_page(poll01)
        poll_page = QuestionnairePage(self.selenium)
        poll_page.select_checkboxes("A")
        poll_page.submit_response()
        self.visit_page(poll01)
        poll_page.select_checkboxes("A")
        poll_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        poll_result = results_page.get_poll_results_text()
        self.assertIn("2", poll_result)

    def test_result_percentage(self):
        poll01 = PollFactory(
            parent=self.section01, 
            owner=self.user,
            result_as_percentage = True
            )
        PollFormFieldFactory(
            page=poll01, 
            required = True,
            choices = "A|B|C",  
            default_value='',  
            field_type='checkboxes', 
        )

        self.visit_page(poll01)
        poll_page = QuestionnairePage(self.selenium)
        poll_page.select_checkboxes("A")
        poll_page.submit_response()
        self.visit_page(poll01)
        poll_page.select_checkboxes("A")
        poll_page.submit_response()
        self.visit_page(poll01)
        poll_page.select_checkboxes("B")
        poll_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        poll_result = results_page.get_poll_results_text()
        self.assertIn("67 %", poll_result)
        self.assertIn("33 %", poll_result)

    def test_multi_select_option_results_for_checkboxes(self):
        poll01 = PollFactory(
            parent=self.section01,
            owner=self.user,
            result_as_percentage=True
            )
        PollFormFieldFactory(
            page=poll01,
            required=True,
            choices="A|B|C",
            default_value='',
            field_type='checkboxes',
        )

        self.visit_page(poll01)
        poll_page = QuestionnairePage(self.selenium)
        poll_page.select_checkboxes("A")
        poll_page.select_checkboxes("B")
        poll_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        poll_result = results_page.get_poll_results_text()

        self.assertIn("A\nYour answer\n100 %", poll_result)
        self.assertIn("B\nYour answer\n100 %", poll_result)
        self.assertIn("C\n0 %", poll_result)
