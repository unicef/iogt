from selenium_tests.base import BaseSeleniumTests
from wagtail.core.models import Site
from iogt_users.factories import AdminUserFactory
from home.factories import SectionFactory, ArticleFactory
from questionnaires.factories import PollFactory
from selenium_tests.pages import QuestionnairePage, SectionPage, ArticlePage

class SectionContentSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.section01 = SectionFactory(parent=self.home, owner=self.user)

    def test_questionnaire(self):
        poll01 = PollFactory(parent=self.section01, owner=self.user)
        self.visit_page(self.section01)
        section_page = SectionPage(self.selenium)
        section_page.navigate_featured_content(poll01.title)
        poll_page = QuestionnairePage(self.selenium)
        self.assertIn(poll01.title, poll_page.title)

    def test_article(self):
        article01 = ArticleFactory(parent=self.section01, owner=self.user)
        self.visit_page(self.section01)
        section_page = SectionPage(self.selenium)
        section_page.navigate_featured_content(article01.title)
        article_page = ArticlePage(self.selenium)
        self.assertIn(article01.title, article_page.title)

    def test_sub_section(self):
        section02 = SectionFactory(parent=self.section01, owner=self.user)
        self.visit_page(self.section01)
        section_page = SectionPage(self.selenium)
        section_page.navigate_featured_content(section02.title)
        section_page2 = SectionPage(self.selenium)
        self.assertIn(section02.title, section_page2.title)
       
    
       

        
    