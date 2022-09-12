from selenium.webdriver.common.by import By

class Locator(object):

#Locators for Home Page
    login_button = "//a[@href='/en/accounts/login/']"
 
#Locators for Login Page 
    login_user_name = "login"
    login_password = "password"
    login_submit = '//button[@type="submit"]'

#Locators for articles
    article_heading = "h1"
    article_lead_image = "article__lead-img-featured"
    article_comment_area = "comment"
    article_reply_comment_area = "comment"
    article_comment_holder = 'comments-holder'
    article_leave_comment = "//input[@value='Leave comment']"
    article_delete_comment = "//a[contains(text(),'Remove')]"
    article_reply_comment = "//a[contains(text(),'Reply')]"
    article_navigate_next = 'article__navigation--next'
    article_navigate_previous = 'article__navigation--previous'

#Locators for base element
    base_element = (By.TAG_NAME, 'html')

#Locator for footer
    footer_element = (By.CSS_SELECTOR, '.footer-main .bottom-level')

#Locator for navbar
    navbar_element = ((By.CSS_SELECTOR, '.footer-main .top-level'))