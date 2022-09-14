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

    def test_title(self):

        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        self.assertIn(self.article01.title, article_page.article_title.text)
        
    def test_image(self):

        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        self.assertTrue(article_page.confirm_image(), 'Image should be present and visible')
        
    
        
        
