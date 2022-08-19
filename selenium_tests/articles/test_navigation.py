import time
from wagtail.core.models import Site
from wagtail_factories import SiteFactory

from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    HomePageFactory,
    SectionFactory,
    ArticleFactory
)

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
        Next = self.selenium.find_element_by_class_name('article__navigation--next')
        Next.click()
        article_title = self.selenium.find_element_by_tag_name('h1').text
        self.assertIn(self.article02.title, article_title)
        

    def test_navigation_previous(self):

        self.visit_page(self.article02)
        Previous = self.selenium.find_element_by_class_name('article__navigation--previous')
        Previous.click()
        article_title = self.selenium.find_element_by_tag_name('h1').text
        self.assertIn(self.article01.title, article_title)
    
        
        
