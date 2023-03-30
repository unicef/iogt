from selenium_tests.base import BaseSeleniumTests
from wagtail.core.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory
from questionnaires.factories import PollFactory, PollFormFieldFactory
from selenium_tests.pages import QuestionnairePage, SectionPage
import home.models as models

class SectionComponentSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)

    def test_featured(self):
        poll01 = PollFactory(parent=self.home, owner=self.user)
        PollFormFieldFactory(page=poll01, field_type='checkboxes', choices='c1|c2|c3', default_value='c2')
        models.FeaturedContent.objects.create(source = self.section01, content = poll01)
        self.visit_page(self.section01)
        section_page = SectionPage(self.selenium)
        section_page.navigate_featured_content(poll01.title)
        poll_page = QuestionnairePage(self.selenium)
        self.assertIn(poll01.title, poll_page.title)
       
    def test_title(self):
        self.visit_page(self.section01)
        section_page = SectionPage(self.selenium)
        self.assertIn(self.section01.title, section_page.title)        
        
    def test_image(self):
        self.visit_page(self.section01)
        article_page = SectionPage(self.selenium)
        self.assertTrue(article_page.has_lead_image(), 'Image should be present and visible')
       

        
    