import time

import home.models as models
from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    BannerIndexPageFactory,
    BannerFactory,
    ArticleFactory
)
from selenium_tests.pages import (
    ArticlePage,
    HomePage)

class BannerSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        self.setup_blank_site()
        self.banner_index = BannerIndexPageFactory(parent=self.site.root_page)
        self.article01 = ArticleFactory(parent = self.site.root_page, title = 'article01')
        self.banner01 = BannerFactory(parent = self.banner_index, title = 'banner01', banner_link_page = self.article01)
        models.HomePageBanner.objects.create(source = self.home, banner_page = self.banner01)


    def test_banner_is_present(self):
        
        self.visit_page(self.home)
        home_page = HomePage(self.selenium)
        self.assertTrue(home_page.has_banner, 'banner should be visible')


    def test_banner_navigation(self):
        
        self.visit_page(self.home)
        home_page = HomePage(self.selenium)  
        home_page.click_banner()
        banner_article = ArticlePage(self.selenium)
        self.assertTrue(
            banner_article.url_matches(self.article01.url),
            'Clicking on banner navigates to correct article'
        )

        

        

