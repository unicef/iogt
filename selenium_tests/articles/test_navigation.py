from wagtail.core.models import Site
from wagtail_factories import SiteFactory
from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    HomePageFactory,
    SectionFactory,
    ArticleFactory
)

from selenium_tests.pages import ArticlePage

class ArticleNavigationSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.home = HomePageFactory()
        self.site = SiteFactory(
            site_name='IoGT',
            hostname=self.host,
            port=self.port,
            is_default_site=True,
            root_page=self.home
        )
        self.section = SectionFactory(parent=self.site.root_page)
        self.article01 = ArticleFactory(parent=self.section, title = 'article01')
        self.article02 = ArticleFactory(parent=self.section, title = 'article02')

    def test_navigation_next(self):

        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.navigate_next()
        article_page = ArticlePage(self.selenium)
        self.assertIn(self.article02.title, article_page.article_title.text)
        

    def test_navigation_previous(self):

        self.visit_page(self.article02)
        article_page = ArticlePage(self.selenium)
        article_page.navigate_previous()
        article_page = ArticlePage(self.selenium)
        self.assertIn(self.article01.title, article_page.article_title.text)
    
        
        
