from typing import List
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium_tests.locators import Locator
from iogt_users.factories import AdminUserFactory, UserFactory


class BasePage(object):

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

        # self.login_button = driver.find_element(By.XPATH, Locator.login_button)

    def url_matches(self, path: str) -> bool:
        return urlparse(self.driver.current_url).path == path

    @property
    def footer(self) -> 'FooterElement':
        return FooterElement(self.driver)

    @property
    def navbar(self) -> 'NavbarElement':
        return NavbarElement(self.driver)


class LoginPage(BasePage):


    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

        self.login_user_name = driver.find_element(By.NAME, Locator.login_user_name)
        self.login_password = driver.find_element(By.NAME, Locator.login_password)
        self.login_submit = driver.find_element(By.XPATH, Locator.login_submit)

    def get_username(self):
        return self.login_user_name
 
    def get_password(self):
        return self.login_password
 
    def get_login_submit(self):
        return self.login_submit

    def login_user(self, user):
        self.login_user_name.send_keys(user.username)
        self.login_password.send_keys('test@123')
        self.login_submit.click()



class ArticlePage(BasePage):

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    @property
    def title(self) -> str:
        return self.driver.find_element(By.TAG_NAME, Locator.article_heading).text

    def has_lead_image(self):
        lead_image = self.driver.find_element(By.CLASS_NAME, Locator.article_lead_image)
        return (
            lead_image.size['width'] > 0
            and lead_image.size['height'] > 0
            and lead_image.is_displayed()
        )
         
    def submit_comment(self, text):
        self.comment_area = self.driver.find_element(By.NAME, Locator.article_comment_area)
        self.comment_area.send_keys(text)
        self.leave_comment_button = self.driver.find_element(By.CSS_SELECTOR, Locator.article_leave_comment)
        self.driver.execute_script("arguments[0].click();", self.leave_comment_button)

    def retrieve_comments(self):
        self.comment_holder = self.driver.find_element(By.CLASS_NAME, Locator.article_comment_holder)
        return self.comment_holder.text

    def delete_last_comment(self):
        self.delete_comment_button = self.driver.find_element(By.XPATH, Locator.article_delete_comment)
        self.driver.execute_script("arguments[0].click();", self.delete_comment_button)

    def reply_last_comment(self, reply):
        self.reply_comment_button = self.driver.find_element(By.XPATH, Locator.article_reply_comment)
        self.driver.execute_script("arguments[0].click();", self.reply_comment_button)
        self.submit_comment(reply)

    def navigate_next(self):
        self.driver.find_element(By.CLASS_NAME, Locator.article_navigate_next).click()   

    def navigate_previous(self):
        self.driver.find_element(By.CLASS_NAME, Locator.article_navigate_previous).click()      


class BaseElement():
    locator = Locator.base_element

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.html = self.driver.find_element(*self.locator)


class FooterElement(BaseElement):
    locator = Locator.footer_element

    @property
    def is_displayed(self) -> bool:
        return self.html.is_displayed()

    @property
    def items(self) -> List['FooterItemElement']:
        return [
            FooterItemElement(self.driver, el)
            for el in self.html.find_elements(By.CSS_SELECTOR, 'nav a')
        ]

class FooterItemElement():
    def __init__(self, driver, el) -> None:
        self.driver = driver
        self.html = el

    @property
    def title(self) -> str:
        return self.html.text

    @property
    def has_icon(self) -> bool:
        icon = self.html.find_element(By.TAG_NAME, 'img')
        return (
            icon.size['width'] > 0
            and icon.size['height'] > 0
            and icon.is_displayed()
        )

    @property
    def background_color(self):
        return self.html.value_of_css_property('background-color')

    @property
    def font_color(self):
        return self.html.value_of_css_property('color')

    def click(self) -> 'BasePage':
        self.html.click()
        return BasePage(self.driver)


class NavbarElement(FooterElement):
    locator = Locator.navbar_element
