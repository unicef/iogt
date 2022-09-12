import time
from wagtail.core.models import Site
from wagtail_factories import SiteFactory
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium_tests.pages import LoginPage

from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    HomePageFactory,
    SectionFactory,
    ArticleFactory,
)
from iogt_users.factories import (
    AdminUserFactory
)

from selenium_tests.pages import ArticlePage

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
        #login as an admin so we can leave a comment
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        login_page = LoginPage(self.selenium)
        login_page.login_admin_user()
        
        #visit an article and leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.submit_comment(test_comment)        
        self.visit_page(self.article01)
        self.assertIn(test_comment, article_page.retrieve_comments())

    def test_remove_article_comment(self):
        #login as an admin so we can leave a comment
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        login_page = LoginPage(self.selenium)
        login_page.login_admin_user()
        
        #visit an article and leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.submit_comment(test_comment)
        self.visit_page(self.article01)

        #delete comment
        article_page.delete_last_comment()
        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn('The comment has been removed successfully!', body_text)

    def test_reply_article_comment(self):
        #login as an admin so we can leave a comment
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        login_page = LoginPage(self.selenium)
        login_page.login_admin_user()
        
        #visit an article and leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.submit_comment(test_comment)        
        
        #leave a reply to the first comment
        test_reply = 'test reply here'
        self.visit_page(self.article01)
        article_page.reply_last_comment(test_reply)
        self.visit_page(self.article01)
        self.assertIn(test_reply, article_page.retrieve_comments())

        

        
        
        
