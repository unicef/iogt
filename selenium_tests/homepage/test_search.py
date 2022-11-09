import time

from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    SectionIndexFactory,
    SectionFactory,
    ArticleFactory
)

from selenium_tests.pages import SearchPage

class SearchSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        self.setup_blank_site()
        self.sections_index = SectionIndexFactory(parent=self.site.root_page)
        self.section01 = SectionFactory(parent = self.sections_index)
        self.article01 = ArticleFactory(parent=self.section01, title = 'Test article for search - asdf;lkj')

    def test_search_bar(self):

        home_page = self.visit_page(self.home)
        home_page.small_search_button_select()
        search_page = SearchPage(self.selenium)
        search_page.search('asdf;lkj')

        
