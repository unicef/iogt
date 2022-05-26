import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from home.factories import ArticleFactory, SectionFactory
from home.models import HomePage
from iogt_users.factories import UserFactory
from comments.models import CommentStatus
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from wagtail.core.models import Page, Site
from home.models import HomePage, Article, Section
from home.wagtail_hooks import limit_page_chooser

class MySeleniumTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):  
        cls.selenium = webdriver.Chrome()
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(MySeleniumTests, cls).tearDownClass()

    def setUp(self):
        self.user = UserFactory()
        self.home_page = HomePage.objects.first()
        self.article01 = ArticleFactory.build(owner=self.user, commenting_status=CommentStatus.OPEN)
        self.home_page.add_child(instance=self.article01)

    def test_article_comment(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/login/'))
        time.sleep(1)
        username_input = self.selenium.find_element_by_name("login")
        username_input.send_keys(self.user.username)
        time.sleep(1)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('test@123')
        time.sleep(1)
        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(1)
        body_text = self.selenium.find_element_by_tag_name('body').text
        assert self.user.username in body_text
        self.selenium.get('%s%s' % (self.live_server_url, '/article0/'))
        time.sleep(1)
        comment_input = self.selenium.find_element_by_name("comment")
        comment_input.send_keys('Test comment')
        time.sleep(1)
        self.selenium.find_element_by_xpath('//input[@value="Leave comment"]').click()
        time.sleep(1)

        
    



    