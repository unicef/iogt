from selenium_tests.base import BaseSeleniumTests
from wagtail.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory, ArticleFactory
from questionnaires.factories import SurveyFactory, SurveyFormFieldFactory
from selenium_tests.pages import QuestionnairePage, QuestionnaireResultsPage

class ArticleEmbeddedSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.article01 = ArticleFactory(parent=self.home, owner=self.user)
        self.section01 = SectionFactory(parent=self.home, owner=self.user)

    def test_simple_embedded(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user, 
            direct_display = True,
            allow_multiple_submissions = False,
            description="[{\"type\": \"paragraph\", \"value\": \"<p>This is a simple survey description</p>\"}]",
            thank_you_text="[{\"type\": \"paragraph\", \"value\": \"<p>Thankyou for completing the survey</p>\"}]" 
            )
        SurveyFormFieldFactory(
            page=survey01, 
            required = True,
            default_value='',  
            field_type='singleline', 
        )
        self.article01.body.append((
            'embedded_survey', {
                'direct_display': survey01.specific.direct_display,
                'survey': survey01,
            }
        ))
        self.visit_page(self.section01)
        #We are looking at an article here, but use the Questionnaire page as we want to test the functionality of the embedded questionnaire
        survey_page = QuestionnairePage(self.selenium)
        self.assertIn("This is a simple survey description", survey_page.get_content_text())
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())
        revisit_page = self.visit_page(self.section01)
        self.assertIn("You have already completed this survey.", revisit_page.get_content_text())

    def test_multiple_page_embedded(self):
        survey01 = SurveyFactory(
            parent=self.section01, 
            owner=self.user,
            direct_display = True,
            multi_step = True,
            description="[{\"type\": \"paragraph\", \"value\": \"<p>This is a simple survey description</p>\"}]",
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
        self.article01.body.append((
            'embedded_survey', {
                'direct_display': survey01.specific.direct_display,
                'survey': survey01,
            }
        ))

        self.visit_page(self.section01)
        #We are looking at an article here, but use the Questionnaire page as we want to test the functionality of the embedded questionnaire
        survey_page = QuestionnairePage(self.selenium)
        self.assertIn("This is a simple survey description", survey_page.get_content_text())
        survey_page.enter_text("Testing some singleline text")
        survey_page.submit_response()
        survey_page.submit_response()
        results_page = QuestionnaireResultsPage(self.selenium)
        self.assertIn("Thankyou for completing the survey", results_page.get_content_text())
        
        
        
        

        
        
