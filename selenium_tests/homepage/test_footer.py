from django.db.utils import Error
from wagtail.core.models import Site
from wagtail_factories import SiteFactory
from selenium.webdriver.common.by import By

from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    FooterIndexPageFactory,
    HomePageFactory,
    SectionFactory,
)

class FooterSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        Site.objects.all().delete()
        self.root_page = HomePageFactory()
        self.site = SiteFactory(
            site_name='IoGT',
            hostname=self.host,
            port=self.port,
            is_default_site=True,
            root_page=self.root_page
        )
        self.footer_index = FooterIndexPageFactory(parent=self.site.root_page)

    def test_footer_is_present(self):
        section = SectionFactory(
            parent=self.footer_index,
            title='Footer Section'
        )

        home_page = BasePage(self.selenium, self.root_page.full_url)
        home_page.visit()
        self.assertTrue(home_page.footer.is_displayed, 'Footer must be visible')
        section_item = home_page.footer.items[0]
        self.assertTrue(section_item.has_icon, 'Icon must be visible')
        self.assertEqual(
            section_item.title,
            section.title,
            'Section title is the link text'
        )
        section_item.click()
        section_page = BasePage(self.selenium, section.full_url)
        self.assertTrue(
            section_page.is_current,
            'Clicking on footer link navigates to section page'
        )


class BasePage():

    def __init__(self, driver, url) -> None:
        self.driver = driver
        self.url = url

    def visit(self) -> None:
        self.driver.get(self.url)

    @property
    def is_current(self):
        return self.driver.current_url.endswith(self.url)

    @property
    def footer(self):
        return FooterElement(self.driver)


class FooterElement():
    locator = (By.CSS_SELECTOR, '.footer-main .bottom-level')

    def __init__(self, driver) -> None:
        self.driver = driver
        self.html = self.driver.find_element(*self.locator)

    @property
    def is_displayed(self):
        return self.html.is_displayed()

    @property
    def items(self):
        return [
            FooterItemElement(el)
            for el in self.html.find_elements(By.CSS_SELECTOR, 'nav a')
        ]


class FooterItemElement():
    def __init__(self, el) -> None:
        self.html = el

    @property
    def title(self):
        return self.html.text

    @property
    def has_icon(self):
        icon = self.html.find_element(By.TAG_NAME, 'img')
        return (
            icon.size['width'] > 0
            and icon.size['height'] > 0
            and icon.is_displayed()
        )

    def click(self) -> None:
        self.html.click()
