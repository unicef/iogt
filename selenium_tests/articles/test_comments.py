from comments.models import CommentStatus
from home.factories import ArticleFactory, SectionFactory
from iogt_users.factories import AdminUserFactory, UserFactory
from selenium_tests.base import BaseSeleniumTests
from selenium_tests.pages import ArticlePage


class ArticleCommentsSeleniumTests(BaseSeleniumTests):
    def setUp(self):
        self.setup_blank_site()
        self.admin = AdminUserFactory()
        self.section = SectionFactory(parent=self.site.root_page)
        self.article01 = ArticleFactory(parent=self.section)

    def test_basic_article_comment(self):
        # login as an admin so we can leave a comment
        login_page = self.visit_login_page()
        login_page.login_user(self.admin)

        # visit an article and leave a comment
        test_comment = "test comment here"
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)
        self.visit_page(self.article01)
        self.assertIn(test_comment, article_page.comments_section.retrieve_comments())

    def test_remove_article_comment(self):
        # login as an admin
        login_page = self.visit_login_page()
        login_page.login_user(self.admin)

        # visit an article and leave a comment
        test_comment = "test comment here"
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)
        self.visit_page(self.article01)

        # delete comment
        article_page.comments_section.delete_last_comment()
        self.assertIn(
            "The comment has been removed successfully!",
            article_page.get_messages_text(),
        )

    def test_user_flagging_comments(self):
        commenter = UserFactory()
        flagger = UserFactory()

        self.visit_login_page().login_user(commenter)
        self.visit_page(self.article01)
        ArticlePage(self.selenium).comments_section.submit_comment("test comment here")
        self.visit_logout_page().logout_user()

        self.visit_login_page().login_user(flagger)
        self.visit_page(self.article01)
        article = ArticlePage(self.selenium)
        article.comments_section.report_last_comment()
        self.visit_page(self.article01)
        self.assertIn(
            "This comment has been reported.", article.comments_section.html.text
        )

    def test_moderator_removing_others_comments(self):
        commenter = UserFactory()

        self.visit_login_page().login_user(commenter)
        self.visit_page(self.article01)
        ArticlePage(self.selenium).comments_section.submit_comment("test comment here")
        self.visit_logout_page().logout_user()

        self.visit_login_page().login_user(self.admin)
        self.visit_page(self.article01)
        article = ArticlePage(self.selenium)
        article.comments_section.delete_last_comment()
        self.assertIn(
            "The comment has been removed successfully!",
            article.get_messages_text(),
        )

    def test_commenting_restrictions(self):
        article_no_comments = ArticleFactory(
            parent=self.section,
            commenting_status=CommentStatus.CLOSED,
        )

        self.visit_login_page().login_user(self.admin)
        self.visit_page(article_no_comments)
        article = ArticlePage(self.selenium)
        self.assertIn(
            "New comments have been disabled for this page",
            article.comments_section.html.text,
        )

    def test_reply_article_comment(self):
        # login as an admin so we can leave a comment
        login_page = self.visit_login_page()
        login_page.login_user(self.admin)

        # visit an article and leave a comment
        test_comment = "test comment here"
        self.visit_page(self.article01)
        article_page = ArticlePage(self.selenium)
        article_page.comments_section.submit_comment(test_comment)

        # leave a reply to the first comment
        test_reply = "test reply here"
        self.visit_page(self.article01)
        article_page.comments_section.reply_last_comment(test_reply)
        self.visit_page(self.article01)
        self.assertIn(test_reply, article_page.comments_section.retrieve_comments())
