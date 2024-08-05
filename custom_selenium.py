import logging
from RPA.Browser.Selenium import Selenium


class CustomSelenium:
    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.browser = Selenium()

    def open_browser(self):
        self.browser.open_available_browser()

    def set_page_size(self, width: int, height: int):
        current_window_size = self.driver.get_window_size()
        html = self.driver.find_element_by_tag_name("html")
        inner_width = int(html.get_attribute("clientWidth"))
        inner_height = int(html.get_attribute("clientHeight"))
        target_width = width + (current_window_size["width"] - inner_width)
        target_height = height + (current_window_size["height"] - inner_height)
        self.driver.set_window_rect(width=target_width, height=target_height)

    def open_url(self, url: str, screenshot: str = None):
        self.browser.go_to(url)
        if screenshot:
            self.browser.capture_page_screenshot(screenshot)

    def driver_quit(self):
        if self.driver:
            self.driver.quit()

    def full_page_screenshot(self, url):
        self.browser.go_to(url)
        page_width = self.driver.execute_script("return document.body.scrollWidth")
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(page_width, page_height)
        self.driver.save_screenshot("screenshot.png")
        self.driver.quit()
