from selenium_tests.base import BaseSeleniumTests
from iogt_users.factories import AdminUserFactory
from selenium_tests.pages import LoginPage
from selenium.webdriver.common.by import By

class LoginSeleniumTests(BaseSeleniumTests):

    def setUp(self):
        
        self.setup_blank_site()
        self.user = AdminUserFactory()
        
    def test_login(self):

        # Tried to test this by clicking the button from the homepage but couldn't get this to work..
        # self.visit_page(self.home)
        # home_page = HomePage(self.selenium)
        # home_page.login_button.click() 

        login_page = self.visit_login_page()        
        login_page.login_user(self.user)
        
        body_text = self.selenium.find_element(By.TAG_NAME, 'body').text
        self.assertIn(self.user.username, body_text)
        
