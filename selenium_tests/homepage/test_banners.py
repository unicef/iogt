from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    BannerIndexPageFactory,
    BannerFactory,
    ArticleFactory
)

class BannerSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        self.setup_blank_site()
        self.banner_index = BannerIndexPageFactory(parent=self.site.root_page)

    def test_banner_is_present(self):
        self.article01 = ArticleFactory(parent = self.site.root_page, title = 'article01')
        self.banner01 = BannerFactory(parent = self.banner_index, title = 'banner01')        

        home_page = self.visit_page(self.home)
        
