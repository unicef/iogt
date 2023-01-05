from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    SectionFactory,
    ArticleFactory
)

from selenium_tests.pages import ArticlePage

class ArticleNavigationSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        self.setup_blank_site()
        self.section = SectionFactory(parent=self.site.root_page)
        self.article01 = ArticleFactory(parent=self.section, title = 'article01')
        self.article02 = ArticleFactory(parent=self.section, title = 'article02')

    def test_navigation_next(self):
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.navigate_next()
        article_page = ArticlePage(self.selenium)
        self.assertIn(self.article02.title, article_page.title)
        

    def test_navigation_previous(self):

        self.visit_page(self.article02)
        article_page = ArticlePage(self.selenium)
        article_page.navigate_previous()
        article_page = ArticlePage(self.selenium)
        self.assertIn(self.article01.title, article_page.title)
    
        
        
