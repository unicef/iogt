import time
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


    def test_title(self):

        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        self.assertIn(self.article01.title, article_page.article_title.text)
        

    def test_image(self):

        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        self.assertTrue(article_page.confirm_image(), 'Image should be present and visible')
        
    
        
        
