from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


class BasePage():

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def url_matches(self, path: str) -> bool:
        return self.driver.current_url.endswith(path)

    @property
    def footer(self) -> 'FooterElement':
        return FooterElement(self.driver)


class FooterElement():
    locator = (By.CSS_SELECTOR, '.footer-main .bottom-level')

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.html = self.driver.find_element(*self.locator)

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

    def click(self) -> 'BasePage':
        self.html.click()
        return BasePage(self.driver)
