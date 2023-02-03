from selenium_tests.base import BaseSeleniumTests
from iogt_users.factories import AdminUserFactory
from selenium_tests.pages import LoginPage
from selenium.webdriver.common.by import By

class LoginSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        
        self.setup_blank_site()
        self.user = AdminUserFactory()
        
    def test_login(self):

        login_page = self.visit_login_page()        
        login_page.login_user(self.user)
    
        self.assertIn(self.user.username, login_page.get_content_text())
        
        
