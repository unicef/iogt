from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    FooterIndexPageFactory,
    SectionFactory,
    SectionIndexFactory,
)

class LayoutSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        self.setup_blank_site()
        self.footer_index = FooterIndexPageFactory(parent=self.site.root_page)
        self.sections_index = SectionIndexFactory(parent=self.site.root_page)
        SectionFactory(
            parent=self.footer_index,
            title='Footers'
        )
        SectionFactory(
            parent=self.sections_index,
            title = 'Sections'
        )                

    def test_page_layout_compact(self):

        home_page = self.visit_page(self.home)
        self.assertTrue(home_page.footer.is_displayed, 'Footer must be visible')
        self.assertTrue(home_page.navbar.is_displayed, 'Navbar must be visible')

        self.assertTrue(home_page.footer_below_navbar_below_content(), 'footer_below_navbar_below_content when screen is compressed')

    def test_page_layout_large(self):
        
        self.selenium.set_window_size(1500, 1000)

        home_page = self.visit_page(self.home)

        self.assertTrue(home_page.footer_rightof_content_rightof_navbar(), 'footer_rightof_content_rightof_navbar when screen is full size')

    
        

        
