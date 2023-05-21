from django.db import connections
from django.conf import settings
from django.core.management import call_command
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from wagtail.core.models import Page, Site
from wagtail_factories import SiteFactory

from home.factories import HomePageFactory
from selenium_tests.pages import BasePage, LoginPage, LogoutPage


class BaseSeleniumTests(LiveServerTestCase):

    fixtures = ['selenium_tests/locales.json']

    host = settings.SE_APP_HOST

    @classmethod
    def setUpClass(cls):
        cls.selenium = create_remote_webdriver()
        super(BaseSeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(BaseSeleniumTests, cls).tearDownClass()

    def visit_page(self, page: Page) -> BasePage:
        self.visit_url(page.url)
        return BasePage(self.selenium)

    def visit_login_page(self) -> LoginPage:
        self.visit_url('/accounts/login/')
        return LoginPage(self.selenium)

    def visit_logout_page(self) -> LogoutPage:
        self.visit_url('/accounts/logout/')
        return LogoutPage(self.selenium)

    def visit_url(self, url: str) -> None:
        url = '%s%s' % (self.live_server_url, url)
        self.selenium.get(url)

    def setup_blank_site(self):
        Site.objects.all().delete()
        self.home = HomePageFactory()
        self.site = SiteFactory(
            site_name='IoGT',
            hostname=self.host,
            port=self.port,
            is_default_site=True,
            root_page=self.home
        )

    # https://github.com/wagtail/wagtail/issues/1824#issuecomment-450575883
    # Identical to TransactionTestCase._fixture_teardown except that 'allow_cascade' is
    # forced.
    def _fixture_teardown(self):
        # Allow TRUNCATE ... CASCADE and don't emit the post_migrate signal
        # when flushing only a subset of the apps
        for db_name in self._databases_names(include_mirrors=False):
            # Flush the database
            inhibit_post_migrate = (
                self.available_apps is not None or
                (   # Inhibit the post_migrate signal when using serialized
                    # rollback to avoid trying to recreate the serialized data.
                    self.serialized_rollback and
                    hasattr(connections[db_name], '_test_serialized_contents')
                )
            )
            call_command('flush', verbosity=0, interactive=False,
                         database=db_name, reset_sequences=False,
                         allow_cascade=True,
                         inhibit_post_migrate=inhibit_post_migrate)


def create_remote_webdriver(preset: str = "chrome") -> webdriver.Remote:
    if preset == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-ssl-errors=yes')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=480,720")
        options.add_argument("--start-maximized")
        driver = webdriver.Remote(
            command_executor=get_hub_url(),
            desired_capabilities=DesiredCapabilities.CHROME,
            options=options,
        )
    elif preset == "firefox":
        options = webdriver.FirefoxOptions()
        driver = webdriver.Remote(
            command_executor=get_hub_url(),
            desired_capabilities=DesiredCapabilities.FIREFOX,
            options=options,
        )
    else:
        raise Exception(
            f"Invalid webdriver preset ('{preset}'); must be 'chrome' or 'firefox'"
        )
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(40)
    return driver


def get_hub_url():
    return f"http://{settings.SE_HUB_HOST}:{settings.SE_HUB_PORT}/wd/hub"
