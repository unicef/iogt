import time
from wagtail.core.models import Site
from wagtail_factories import SiteFactory
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    HomePageFactory,
    SectionFactory,
    ArticleFactory,
)
from iogt_users.factories import (
    AdminUserFactory
)

class ArticleCommentsSeleniumTests(BaseSeleniumTests):

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
        self.user = AdminUserFactory()
        self.section = SectionFactory(parent=self.site.root_page)
        self.article01 = ArticleFactory(parent=self.section, title = 'article01')

    def test_basic_article_comment(self):
        #login so we can leave a comment
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys(self.user.username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test@123')
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        
        #visit an article and leave a comment
        self.visit_page(self.article01)        
        comment_input = self.selenium.find_element_by_name("comment")
        comment_input.send_keys('test comment here')
        button = self.selenium.find_element_by_xpath("//input[@value='Leave comment']")
        self.selenium.execute_script("arguments[0].click();", button)
        self.visit_page(self.article01)
        comment_section = self.selenium.find_element_by_class_name('comments-holder').text
        self.assertIn('test comment here', comment_section)
        
        
        
