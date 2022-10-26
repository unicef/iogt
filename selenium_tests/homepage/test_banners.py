from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    FooterIndexPageFactory,
    SectionFactory,
    SectionIndexFactory,
)

class BannerSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        self.setup_blank_site()
        
