from wagtail.core.models import Site
from wagtail_factories import SiteFactory

from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    FooterIndexPageFactory,
    HomePageFactory,
    SectionFactory,
    SectionIndexFactory,
)

class FooterSeleniumTests(BaseSeleniumTests):

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
        self.footer_index = FooterIndexPageFactory(parent=self.site.root_page)
        self.sections_index = SectionIndexFactory(parent=self.site.root_page)

    def test_footer_is_present(self):
        section = SectionFactory(
            parent=self.footer_index,
            title='Footer Section'
        )

        home_page = self.visit_page(self.home)
        self.assertTrue(home_page.footer.is_displayed, 'Footer must be visible')
        section_item = home_page.footer.items[0]
        self.assertTrue(section_item.has_icon, 'Icon must be visible')
        self.assertEqual(
            section_item.title,
            section.title,
            'Section title is the link text'
        )
        section_page = section_item.click()
        self.assertTrue(
            section_page.url_matches(section.url),
            'Clicking on footer link navigates to section page'
        )

    def test_navbar_is_present(self):
        section = SectionFactory(
            parent=self.sections_index,
            background_color='#0A0',
            font_color='#DDD',
        )

        home_page = self.visit_page(self.home)
        self.assertTrue(home_page.navbar.is_displayed, 'Navbar must be visible')
        item = home_page.navbar.items[0]
        self.assertTrue(item.has_icon, 'Icon must be visible')
        self.assertEqual(
            item.title,
            section.title,
            'Section title is the link text'
        )
        self.assertEqual(
            item.background_color,
            'rgba(0, 170, 0, 1)',
            'Navbar item background color must match section background color'
        )
        self.assertEqual(
            item.font_color,
            'rgba(221, 221, 221, 1)',
            'Navbar item font color must match section font color'
        )
        section_page = item.click()
        self.assertTrue(
            section_page.url_matches(section.url),
            'Clicking on footer link navigates to section page'
        )
