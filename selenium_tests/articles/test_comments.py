from selenium.webdriver.common.by import By
from selenium_tests.base import BaseSeleniumTests
from home.factories import (
    SectionFactory,
    ArticleFactory,   
)
from comments.models import CommentStatus
from iogt_users.factories import (
    AdminUserFactory,
    UserFactory
)
from selenium_tests.pages import ArticlePage

class ArticleCommentsSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        self.setup_blank_site()
        self.user = AdminUserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.section = SectionFactory(parent=self.site.root_page)
        self.article01 = ArticleFactory(parent=self.section, title = 'article01')
        self.article02 = ArticleFactory(parent=self.section, title = 'article02', commenting_status = CommentStatus.CLOSED)

    def test_basic_article_comment(self):
        #login as an admin so we can leave a comment
        login_page = self.visit_login_page()
        login_page.login_user(self.user)
        
        #visit an article and leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)
        self.visit_page(self.article01)
        self.assertIn(test_comment, article_page.comments_section.retrieve_comments())

    def test_remove_article_comment(self):
        #login as an admin
        login_page = self.visit_login_page()
        login_page.login_user(self.user)
        
        #visit an article and leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)
        self.visit_page(self.article01)

        #delete comment
        article_page.comments_section.delete_last_comment()
        self.assertIn('The comment has been removed successfully!', article_page.get_messages_text())

    def test_user_flagging_comments(self):
        #login as a normal user
        login_page = self.visit_login_page()
        login_page.login_user(self.user2)
        #leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)
        #logout
        logout_page = self.visit_logout_page()
        logout_page.logout_user()
        #log in as a different user
        login_page = self.visit_login_page()
        login_page.login_user(self.user3)
        #Go to article and report comment
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.report_last_comment()
        self.visit_page(self.article01)
        self.assertIn('This comment has been reported.', article_page.comments_section.html.text)

    def test_moderator_removing_others_comments(self):
        #login as a normal user
        login_page = self.visit_login_page()
        login_page.login_user(self.user2)
        #leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)
        #logout
        logout_page = self.visit_logout_page()
        logout_page.logout_user()
        #log in as an admin user
        login_page = self.visit_login_page()
        login_page.login_user(self.user)
        #Go to article and remove comment
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.delete_last_comment()
        self.assertIn('The comment has been removed successfully!', article_page.get_messages_text())

    def test_commenting_restrictions(self):
        #login as a normal user
        login_page = self.visit_login_page()
        login_page.login_user(self.user)
        self.visit_page(self.article02)
        article_page = ArticlePage(self.selenium)
        self.assertIn('New comments have been disabled for this page', article_page.comments_section.html.text)        

    def test_reply_article_comment(self):
        #login as an admin so we can leave a comment
        login_page = self.visit_login_page()
        login_page.login_user(self.user)
        
        #visit an article and leave a comment
        test_comment = 'test comment here'
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)        
        
        #leave a reply to the first comment
        test_reply = 'test reply here'
        self.visit_page(self.article01)
        article_page.comments_section.reply_last_comment(test_reply)
        self.visit_page(self.article01)
        self.assertIn(test_reply, article_page.comments_section.retrieve_comments())

        

        
        
        
