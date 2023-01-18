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

    def test_footer_is_present(self):
        footer = SectionFactory(
            parent=self.footer_index,
            title='Footers'
        )        
    
        section = SectionFactory(
            parent=self.sections_index,
            title = 'Sections'
        )

        home_page = self.visit_page(self.home)
        self.assertTrue(home_page.footer.is_displayed, 'Footer must be visible')
        self.assertTrue(home_page.navbar.is_displayed, 'Navbar must be visible')

        self.assertTrue(home_page.navbar_below_content(), 'Navbar should be below footer when page is compressed')
        self.assertTrue(home_page.footers_below_navbar(), 'Footer should be below navbar when page is compressed')

    
        

        
