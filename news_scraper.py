import os
import re
from datetime import datetime
from time import sleep
from typing import List, Tuple, Union

from RPA.HTTP import HTTP
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement

from logger_config import verbose_logger
from custom_selenium import CustomSelenium


class NewsScraper(CustomSelenium):
    def __init__(self, search_phrase: str, category: str, months: int):
        super().__init__()
        self.http = HTTP()
        self.search_phrase = search_phrase
        self.category = category
        self.months = months

    def _check_no_results(self) -> bool:
        div_results_element = "css:div.search-results-module-ajax"
        no_results_element = "css:div.search-results-module-no-results"

        self.browser.wait_until_element_is_visible(div_results_element)
        return self.browser.is_element_visible(no_results_element)

    def search_and_filter_news(self) -> None:
        search_btn_element = "css:button[data-element='search-button']"
        search_input_element = "css:input[data-element='search-form-input']"
        select_input_element = "css:select.select-input"
        option_newest_element = "xpath://option[text()='Newest']"

        self.browser.wait_until_element_is_visible(search_btn_element, timeout=10)
        verbose_logger.info("Clicking search button.")
        self.browser.click_button(search_btn_element)

        verbose_logger.info(f"Entering search phrase: {self.search_phrase}")
        self.browser.input_text(search_input_element, self.search_phrase)
        self.browser.press_key(search_input_element, "\ue007")  # press enter

        if self._check_no_results():
            error_message = (
                f"No results found for the search phrase '{self.search_phrase}'"
            )
            raise ValueError(error_message)

        if self.category:
            self._filter_by_category()

        try:
            self.browser.wait_until_element_is_visible(select_input_element, timeout=10)
            verbose_logger.info("Selecting 'Newest' option.")
            self.browser.click_element(select_input_element)
            self.browser.wait_until_element_is_visible(
                option_newest_element, timeout=10
            )
            self.browser.click_element(option_newest_element)
            sleep(5)
        except Exception as e:
            verbose_logger.warning(
                f"Option 'Newest' not found or could not set selected property. Exception: {str(e)}"
            )

    def _filter_by_category(self) -> None:
        category_checkbox_element = f"//label[contains(@class, 'checkbox-input-label')]//span[translate(text(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')='{self.category.upper()}']"
        filters_open_button = "css:.button.filters-open-button"
        apply_button = "css:.button.apply-button"
        try:
            if self.browser.is_element_visible(filters_open_button):
                verbose_logger.info(f"Opening filters for category: {self.category}")
                self.browser.click_element(filters_open_button)
            self.browser.wait_until_element_is_visible(
                category_checkbox_element, timeout=10
            )
        except Exception as e:
            verbose_logger.warning(
                f"Category '{self.category}' not found. Exception: {str(e)}"
            )

        try:
            self.browser.wait_until_element_is_visible(
                category_checkbox_element, timeout=10
            )
            verbose_logger.info(f"Selecting category: {self.category}")
            self.browser.click_element(category_checkbox_element)

            if self.browser.is_element_visible(filters_open_button):
                self.browser.wait_until_element_is_visible(apply_button, timeout=10)
                verbose_logger.info("Applying category filter.")
                self.browser.click_element(apply_button)
            sleep(5)
        except Exception as e:
            verbose_logger.warning(
                f"Category '{self.category}' not found. Exception: {str(e)}"
            )

    def _is_element_stale(self, element: WebElement) -> bool:
        try:
            element.get_attribute("outerHTML")
            return False
        except StaleElementReferenceException:
            return True

    def _wait_until_not_stale(self, locator: str) -> WebElement:
        self.browser.wait_until_page_contains_element(locator, timeout=30)
        element = self.browser.find_element(locator)
        self.browser.wait_until_element_is_visible(element, timeout=30)
        return element

    def get_news(self) -> List[dict]:
        news = []
        not_month_limit = True
        next_page = True
        article_element = "css:div[class='promo-wrapper']"

        while not_month_limit:
            try:
                verbose_logger.info("Waiting for articles to be visible.")
                self.browser.wait_until_element_is_visible(article_element, timeout=20)
                articles = self.browser.find_elements(article_element)

                for article in articles:
                    try:
                        if self._is_element_stale(article):
                            verbose_logger.info("Waiting for stale element to refresh.")
                            article = self._wait_until_not_stale(article_element)
                        news_obj = self._process_article(article)
                        if not news_obj:
                            not_month_limit = False
                            next_page = False
                            break
                        news.append(news_obj)
                    except Exception as e:
                        verbose_logger.warning(f"Failed to process article: {str(e)}")
                        continue
                if next_page:
                    self._goto_next_page()
            except Exception as e:
                verbose_logger.warning(f"Failed to find articles: {str(e)}")
                break

        return news

    def _process_article(self, article: WebElement) -> Union[dict, None]:
        try:
            news_obj = {
                "title": "N/A",
                "description": "N/A",
                "date": "N/A",
                "picture_filename": "N/A",
                "picture_path": "N/A",
                "search_phrase_count": 0,
                "contains_money": False,
            }

            news_obj["date"], within_months = self._get_date_news(article)
            if not within_months:
                return None

            news_obj["title"] = self._get_title_news(article)
            news_obj["description"] = self._get_description_news(article)
            news_obj["picture_path"], news_obj["picture_filename"] = (
                self._get_image_news(article, news_obj["title"])
            )
            news_obj["search_phrase_count"] = self._count_search_phrase(
                news_obj["title"], news_obj["description"]
            )
            news_obj["contains_money"] = self._contains_money(
                news_obj["title"]
            ) or self._contains_money(news_obj["description"])

            return news_obj
        except Exception as e:
            verbose_logger.warning(f"Failed to process article: {str(e)}")
            return None

    def _goto_next_page(self) -> None:
        next_page = "//div[contains(@class, 'search-results-module-next-page')]//a[@rel='nofollow']"
        try:
            verbose_logger.info("Going to next page.")
            self.browser.wait_until_element_is_visible(next_page, timeout=10)
            self.browser.click_element(next_page)
        except Exception as e:
            raise ValueError(e)

    def _get_date_news(self, article: WebElement) -> Tuple[Union[str, None], bool]:
        current_date = datetime.now()
        current_year_month = (current_date.year, current_date.month)
        try:
            date_timestamp = article.find_element(
                "css selector", "p[data-timestamp]"
            ).get_attribute("data-timestamp")
            article_date = datetime.fromtimestamp(int(date_timestamp) / 1000.0)
            article_year_month = (article_date.year, article_date.month)

            month_diff = (current_year_month[0] - article_year_month[0]) * 12 + (
                current_year_month[1] - article_year_month[1]
            )

            if month_diff >= self.months:
                return None, False

            return str(article_date.strftime("%m/%d/%Y")), True
        except Exception as e:
            verbose_logger.warning(f"Date not found in article. Exception: {str(e)}")
            return "N/A", True

    def _get_title_news(self, article: WebElement) -> str:
        try:
            return article.find_element("css selector", "h3.promo-title a").text
        except Exception as e:
            verbose_logger.warning(f"Title not found in article. Exception: {str(e)}")
            return "N/A"

    def _get_description_news(self, article: WebElement) -> str:
        try:
            description_element = article.find_element(
                "css selector", "p.promo-description"
            )
            return description_element.text if description_element else "N/A"
        except Exception:
            verbose_logger.info("Description not found in article.")
            return "N/A"

    def _get_image_news(self, article: WebElement, title: str) -> Tuple[str, str]:
        try:
            image_element = article.find_element("css selector", "div.promo-media img")
            image_url = image_element.get_attribute("src")
            filename = self._regex(str(title).lower()).replace(" ", "-")
            image_filename = f"{filename}.png"
            download_path = f"output/{image_filename}"

            image_abs_path = os.path.join(os.getcwd(), download_path)

            self._download_image(image_url, download_path)
            return image_abs_path, image_filename
        except Exception as e:
            verbose_logger.warning(
                f"Image not found in article or failed to download. Exception: {str(e)}"
            )
            return "N/A", "N/A"

    def _download_image(self, image_url: str, file_path: str) -> None:
        try:
            verbose_logger.info(f"Downloading image from {image_url}")
            self.http.download(image_url, file_path)
        except Exception as e:
            verbose_logger.warning(
                f"Failed to download image from {image_url}. Exception: {str(e)}"
            )

    @staticmethod
    def _regex(text: str) -> str:
        return re.sub(r"[^A-Za-z0-9\s]+", "", text)

    def _count_search_phrase(self, title: str, description: str) -> int:
        search_phrase_count = title.lower().count(self.search_phrase.lower())
        search_phrase_count += description.lower().count(self.search_phrase.lower())
        return search_phrase_count

    @staticmethod
    def _contains_money(text: str) -> bool:
        money_pattern = re.compile(
            r"\$\d+(\.\d{1,2})?|(\d{1,3}(,\d{3})*(\.\d{2})?)? (dollars|USD)",
            re.IGNORECASE,
        )
        return bool(money_pattern.search(text))
