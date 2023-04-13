from typing import List
from urllib.parse import urlparse

from django.urls import reverse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.relative_locator import locate_with
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
from wagtail.tests.utils import WagtailPageTests

def safe_click(driver, button):
    try:
        button.click()
    except WebDriverException:
        driver.execute_script("arguments[0].click();", button)

def visible_with_size(item):
    return (
        item.size['width'] > 0
        and item.size['height'] > 0
        and item.is_displayed()
    )
class BasePage(object):

    body_text_locator = (By.TAG_NAME, 'body')
    content_text_locator = (By.CLASS_NAME, 'content')
    message_text_locator = (By.CLASS_NAME, 'messages')
    search_button_locator = (By.CLASS_NAME, 'xs-home-header__search')
    navbar_locator = (By.CSS_SELECTOR, '.top-level')
    footer_locator = (By.CSS_SELECTOR, '.bottom-level')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver        

    def url_matches(self, path: str) -> bool:
        return urlparse(self.driver.current_url).path == path

    def get_body_text(self):
        return self.driver.find_element(*self.body_text_locator).text

    def get_content_text(self):
        return self.driver.find_element(*self.content_text_locator).text

    def get_messages_text(self):
        return self.driver.find_element(*self.message_text_locator).text

    def small_search_button_select(self):
        return self.driver.find_element(*self.search_button_locator).click()
    
    def footer_below_navbar_below_content(self):
        content = self.driver.find_element(*self.content_text_locator)
        navbar = self.driver.find_element(locate_with(*self.navbar_locator).below(content))
        footer = self.driver.find_element(locate_with(*self.footer_locator).below(navbar))
        if navbar.is_displayed() and footer.is_displayed():
            return True
        else:
            return False
    
    def footer_rightof_content_rightof_navbar(self):
        navbar = self.driver.find_element(*self.navbar_locator)
        content = self.driver.find_element(locate_with(*self.content_text_locator).to_right_of(navbar))        
        footer = self.driver.find_element(locate_with(*self.footer_locator).to_right_of(content))
        if content.is_displayed() and footer.is_displayed():
            return True
        else:
            return False

    @property
    def footer(self) -> 'FooterElement':
        return FooterElement(self.driver)

    @property
    def navbar(self) -> 'NavbarElement':
        return NavbarElement(self.driver)

class HomePage(BasePage):

    banner_area_locator = (By.CSS_SELECTOR, "section[class='banner-holder']")
    banner_image_locator = (By.CSS_SELECTOR, "img[alt='An image']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def has_banner(self):
        banner = self.driver.find_element(*self.banner_area_locator)
        print()
        return visible_with_size(banner)            
    
    def click_banner(self):
        banner_image = self.driver.find_element(*self.banner_image_locator)
        banner_image.click()


class LoginPage(BasePage):    

    user_name_locator = (By.NAME, 'login')
    password_locator = (By.NAME, 'password')
    submit_locator = (By.CSS_SELECTOR, "button[type='Submit']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        
        self.login_user_name = driver.find_element(*self.user_name_locator)
        self.login_password = driver.find_element(*self.password_locator)
        self.login_submit = driver.find_element(*self.submit_locator)

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

class LogoutPage(BasePage):    

    logout_button_locator = (By.CSS_SELECTOR, "button[type='Submit']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        
        self.logout_submit = driver.find_element(*self.logout_button_locator)

    def logout_user(self):
        self.logout_submit.click()

class SearchPage(BasePage):
      
    search_area_locator = (By.CLASS_NAME, "profile-form__input")
    search_button_locator = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver      
        self.search_area = self.driver.find_element(*self.search_area_locator)
        self.search_submit = driver.find_element(*self.search_button_locator)

    def search(self, searchtext):
       
        self.search_area.send_keys(searchtext)
        self.search_submit.click()

class ArticlePage(BasePage):

    heading_locator = (By.TAG_NAME, 'h1')
    lead_image_locator = (By.CLASS_NAME, 'article__lead-img-featured')
    navigate_next_locator = (By.CLASS_NAME, 'article__navigation--next')
    navigate_previous_locator = (By.CLASS_NAME, 'article__navigation--previous')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    @property
    def comments_section(self) -> 'CommentsSectionElement':
        return CommentsSectionElement(self.driver)
        
    @property
    def title(self) -> str:
        return self.driver.find_element(*self.heading_locator).text

    def has_lead_image(self):
        lead_image = self.driver.find_element(*self.lead_image_locator)
        return visible_with_size(lead_image)
         
    def navigate_next(self):

        safe_click(self.driver, self.driver.find_element(*self.navigate_next_locator))
        return BasePage(self.driver)  

    def navigate_previous(self):
        safe_click(self.driver, self.driver.find_element(*self.navigate_previous_locator))
        return BasePage(self.driver)

class SectionPage(BasePage):

    heading_locator = (By.CLASS_NAME, 'image-overlay__text')
    lead_image_locator = (By.CLASS_NAME, 'lead-img')
    

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        
    @property
    def title(self) -> str:
        return self.driver.find_element(*self.heading_locator).text

    def has_lead_image(self):
        lead_image = self.driver.find_element(*self.lead_image_locator)
        return visible_with_size(lead_image)
         
    def navigate_featured_content(self, LinkText):
        safe_click(self.driver, self.driver.find_element(By.PARTIAL_LINK_TEXT, LinkText))

class QuestionnairePage(BasePage):

    heading_locator = (By.TAG_NAME, 'h1')
    checkbox_locator = (By.CSS_SELECTOR, "input[type='checkbox']")
    date_locator = (By.CSS_SELECTOR, "input[type='date']")
    date_time_locator = (By.CSS_SELECTOR, "input[type='datetime-local']")
    dropdown_locator = (By.CLASS_NAME, 'quest-item__input')
    email_locator = (By.CSS_SELECTOR, "input[type='email']")
    text_locator = (By.CLASS_NAME, 'cust-input')
    number_locator = (By.CSS_SELECTOR, "input[type='number']")
    radio_locator = (By.CSS_SELECTOR, "input[type='radio']")
    url_locator = (By.CSS_SELECTOR, "input[type='url']")
    submit_locator = (By.CSS_SELECTOR, "button[type='submit']")
    login_submit_locator = (By.PARTIAL_LINK_TEXT, "Log in to participate")

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        
    @property
    def title(self) -> str:
        return self.driver.find_element(*self.heading_locator).text

    def submit_response(self):
        safe_click(self.driver,self.driver.find_element(*self.submit_locator))

    def login_button_submit(self):
        safe_click(self.driver,self.driver.find_element(*self.login_submit_locator))

    def select_checkbox(self):
        self.driver.find_element(*self.checkbox_locator).click()

    def select_checkboxes(self, option):
        safe_click(self.driver, self.driver.find_element(By.CSS_SELECTOR, "input[value='" + option + "']"))

    def enter_date(self, date):
        date_input = self.driver.find_element(*self.date_locator)
        date_input.click()
        date_input.send_keys(date)

    def enter_date_time(self, date, time):
        date_input = self.driver.find_element(*self.date_time_locator)
        safe_click(self.driver, date_input)
        date_input.send_keys(date)
        date_input.send_keys(Keys.TAB)
        date_input.send_keys(time)

    def use_dropdown(self, question, selection):
        select = Select(self.driver.find_element(By.NAME,question))
        select.select_by_visible_text(selection)
        return select.first_selected_option.text

    def enter_email(self, email):
        input = self.driver.find_element(*self.email_locator)
        input.send_keys(email)

    def enter_text(self, text):
        input = self.driver.find_element(*self.text_locator)
        detailinput = input.find_element(By.CSS_SELECTOR, "input[type='text']")
        detailinput.send_keys(text)

    def enter_multiline_text(self, text):
        input = self.driver.find_element(*self.text_locator)
        detailinput = input.find_element(By.CSS_SELECTOR, "textarea")
        detailinput.send_keys(text)

    def enter_number(self, number):
        input = self.driver.find_element(*self.number_locator)
        input.send_keys(number)

    def select_radio(self, option):
        self.driver.find_element(By.CSS_SELECTOR, "input[value='" + option + "']").click()

    def enter_url(self, url):
        input = self.driver.find_element(*self.url_locator)
        input.send_keys(url)

class QuestionnaireResultsPage(BasePage):

    poll_result_locator = (By.CLASS_NAME, 'polls-widget__form')
    quiz_result_locator = (By.CLASS_NAME, 'quiz-answer-banner__answers')
    back_button_locator = (By.PARTIAL_LINK_TEXT, 'Back')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def get_poll_results_text(self):
        return self.driver.find_element(*self.poll_result_locator).text

    def get_quiz_results_text(self):
        return self.driver.find_element(*self.quiz_result_locator).text

    def go_back(self):
        safe_click(self.driver, self.driver.find_element(*self.back_button_locator))

class BaseElement():
    locator = (By.TAG_NAME, 'html')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.html = self.driver.find_element(*self.locator)

    @property
    def is_displayed(self) -> bool:
        return self.html.is_displayed()

class CommentsSectionElement(BaseElement):
    locator =  (By.CLASS_NAME, 'comments')

    comment_area_locator = (By.NAME, "comment")
    reply_comment_area_locator = (By.NAME, "comment")
    comment_holder_locator = (By.CLASS_NAME, 'comments-holder')
    leave_comment_locator = (By.CSS_SELECTOR, "input[value='Leave comment']")
    delete_comment_locator = (By.LINK_TEXT, 'Remove')
    reply_comment_locator = (By.LINK_TEXT,'Reply')
    report_comment_locator = (By.LINK_TEXT,'Report') 
    report_button_locator = (By.CSS_SELECTOR, "input[value='Report']")

    def submit_comment(self, text):
        self.comment_area = self.driver.find_element(*self.comment_area_locator)
        self.comment_area.send_keys(text)
        safe_click(self.driver, self.driver.find_element(*self.leave_comment_locator))

    def retrieve_comments(self):
        self.comment_holder = self.driver.find_element(*self.comment_holder_locator)
        return self.comment_holder.text

    def delete_last_comment(self):
        safe_click(self.driver, self.driver.find_element(*self.delete_comment_locator))

    def reply_last_comment(self, reply):
        safe_click(self.driver, self.driver.find_element(*self.reply_comment_locator))
        self.submit_comment(reply)

    def report_last_comment(self):
        safe_click(self.driver, self.driver.find_element(*self.report_comment_locator))
        self.driver.find_element(*self.report_button_locator).click()
    

class FooterElement(BaseElement):
    locator = (By.CSS_SELECTOR, '.footer-main .bottom-level')

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
        return visible_with_size(icon)

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
    locator = (By.CSS_SELECTOR, '.footer-main .top-level')


class WagtailAdminPage(object):
    submit_locator = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver: WebDriver) -> None:
        super().__init__()
        self.driver = driver

    def select_skip_logic(self, skip_logic):
        selected_skip_logic = Select(self.driver.find_element(By.ID, skip_logic))
        selected_skip_logic.select_by_value("question")

    def select_skip_logic_question(self, question, selection):
        select_question = Select(self.driver.find_element(By.ID, question))
        select_question.select_by_value(selection)

    def submit_response(self):
        safe_click(self.driver, self.driver.find_elements(*self.submit_locator)[1])
