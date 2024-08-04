import logging
import os
import re
from datetime import datetime

from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.Robocorp.WorkItems import WorkItems
from selenium.webdriver.common.keys import Keys

from CustomSelenium import CustomSelenium

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class WorkItemLoader:
    def __init__(self, work_items):
        self.work_items = work_items
        self.search_phrase = ""
        self.category = ""
        self.months = 0

    def load(self):
        try:
            self.work_items.get_input_work_item()
            work_item_data = self.work_items.get_work_item_variables()

            self.search_phrase = self._get_mandatory_value(
                work_item_data, "search_phrase"
            )
            self.category = work_item_data.get("category", None)
            self.months = self._get_months(work_item_data)
        except Exception as e:
            logging.error(f"Failed to load work items: {str(e)}")
            raise ValueError(e)

    def _get_mandatory_value(self, data, key):
        try:
            value = data[key]
            if not value:
                raise ValueError(
                    f"The '{key}' is mandatory and was not provided in the work item."
                )
            return value
        except KeyError:
            logging.error(
                f"The '{key}' is mandatory and was not provided in the work item."
            )
            raise ValueError(
                f"The '{key}' is mandatory and was not provided in the work item."
            )

    def _get_months(self, data):
        try:
            months = int(data.get("months", 0))
            if months < 0:
                logging.warning(
                    "The 'months' provided is less than 0. Defaulting to 1."
                )
                return 1
            return months if months > 0 else 1
        except ValueError:
            logging.warning(
                "The 'months' is not a valid integer in the work item, defaulting to 1."
            )
            return 1



    def search_and_filter_news(self):
        search_btn_element = "css:button[data-element='search-button']"
        search_input_element = "css:input[data-element='search-form-input']"
        select_input_element = "css:select.select-input"
        option_newest_element = "xpath://option[text()='Newest']"

        self.browser.wait_until_element_is_visible(search_btn_element, timeout=10)
        self.browser.click_button(search_btn_element)
        self.browser.input_text(search_input_element, self.search_phrase)
        self.browser.press_key(search_input_element, Keys.ENTER)

        if self.category:
            category_checkbox_element = f"//label[contains(@class, 'checkbox-input-label')]//span[text()='{self.category}']"
            filters_open_button = "css:.button.filters-open-button"
            apply_button = "css:.button.apply-button"
            try:
                if self.browser.is_element_visible(filters_open_button):
                    self.browser.click_element(filters_open_button)
                self.browser.wait_until_element_is_visible(
                    category_checkbox_element, timeout=10
                )
            except Exception as e:
                logging.warning(
                    f"Category '{self.category}' not found. Exception: {str(e)}"
                )
            try:
                self.browser.wait_until_element_is_visible(
                    category_checkbox_element, timeout=10
                )
                self.browser.click_element(category_checkbox_element)

                if self.browser.is_element_visible(filters_open_button):
                    self.browser.wait_until_element_is_visible(apply_button, timeout=10)
                    self.browser.click_element(apply_button)
            except Exception as e:
                logging.warning(
                    f"Category '{self.category}' not found. Exception: {str(e)}"
                )
        try:
            self.browser.wait_until_element_is_visible(select_input_element, timeout=10)
            self.browser.click_element(select_input_element)

            self.browser.wait_until_element_is_visible(
                option_newest_element, timeout=10
            )
            self.browser.click_element(option_newest_element)
            self.browser.wait_until_element_is_not_visible(
                option_newest_element, timeout=10
            )
        except Exception as e:
            logging.warning(
                f"Option 'Newest' not found or could not set selected property. Exception: {str(e)}"
            )

    def get_news(self):
        news = []
        not_month_limit = True
        article_element = "css:div[class='promo-wrapper']"

        while not_month_limit:
            try:
                self.browser.wait_until_element_is_visible(article_element, timeout=10)
                articles = self.browser.find_elements(article_element)

                for article in articles:
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

                        news_obj["date"], not_month_limit = self.get_date_news(article)
                        if not not_month_limit:
                            break

                        news_obj["title"] = self.get_title_news(article)
                        news_obj["description"] = self.get_description_news(article)
                        news_obj["picture_path"], news_obj["picture_filename"] = (
                            self.get_image_news(article, news_obj["title"])
                        )
                        news_obj["search_phrase_count"] = self.count_search_phrase(
                            news_obj["title"], news_obj["description"]
                        )
                        news_obj["contains_money"] = self.contains_money(
                            news_obj["title"]
                        ) or self.contains_money(news_obj["description"])

                        news.append(news_obj)
                    except Exception as e:
                        logging.warning(f"Failed to process article: {str(e)}")
                        continue

                self.goto_next_page()
            except Exception as e:
                logging.warning(f"Failed to find articles: {str(e)}")
                break

        return news

    def goto_next_page(self):
        next_page = "//div[contains(@class, 'search-results-module-next-page')]//a[@rel='nofollow']"
        try:
            self.browser.wait_until_element_is_visible(next_page, timeout=10)
            self.browser.click_element(next_page)
        except Exception as e:
            logging.warning(
                f"Next page element not found or click failed. Exception: {str(e)}"
            )

    def get_date_news(self, article):
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
            logging.warning(f"Date not found in article. Exception: {str(e)}")
            return "N/A", True

    def get_title_news(self, article):
        try:
            return article.find_element("css selector", "h3.promo-title a").text
        except Exception as e:
            logging.warning(f"Title not found in article. Exception: {str(e)}")
            return "N/A"

    def get_description_news(self, article):
        try:
            return article.find_element("css selector", "p.promo-description").text
        except Exception as e:
            logging.warning(f"Description not found in article. Exception: {str(e)}")
            return "N/A"

    def get_image_news(self, article, title):
        try:
            image_element = article.find_element("css selector", "div.promo-media img")
            image_url = image_element.get_attribute("src")
            filename = self.regex(str(title).lower()).replace(" ", "-")
            image_filename = f"{filename}.png"
            download_path = f"output/{image_filename}"

            image_abs_path = os.path.join(os.getcwd(), download_path)

            self.download_image(image_url, download_path)
            return image_abs_path, image_filename
        except Exception as e:
            logging.warning(
                f"Image not found in article or failed to download. Exception: {str(e)}"
            )
            return "N/A", "N/A"

    def download_image(self, image_url, file_path):
        try:
            self.http.download(image_url, file_path)
        except Exception as e:
            logging.warning(
                f"Failed to download image from {image_url}. Exception: {str(e)}"
            )

    def regex(self, text):
        return re.sub(r"[^A-Za-z0-9\s]+", "", text)

    def count_search_phrase(self, title, description):
        search_phrase_count = title.lower().count(self.search_phrase.lower())
        search_phrase_count += description.lower().count(self.search_phrase.lower())
        return search_phrase_count

    def contains_money(self, text):
        money_pattern = re.compile(
            r"\$\d+(\.\d{1,2})?|(\d{1,3}(,\d{3})*(\.\d{2})?)? (dollars|USD)",
            re.IGNORECASE,
        )
        return bool(money_pattern.search(text))

    def save_to_excel(self, news):
        try:
            if not news:
                logging.warning("No news data to save.")
                return
            excel_filename = self.search_phrase.lower().replace(" ", "-")
            self.excel.create_workbook(f"output/news_{excel_filename}.xlsx")
            self.excel.append_rows_to_worksheet(news, header=True)
            self.excel.save_workbook()
        except Exception as e:
            logging.error(f"Failed to save news to Excel: {str(e)}")

    def run(self, url):
        try:
            self.open_website(url)
            self.search_and_filter_news()
            news = self.get_news()
            self.save_to_excel(news)
        except Exception as e:
            logging.error(f"An error occurred during execution: {str(e)}")
        finally:
            self.driver_quit()


if __name__ == "__main__":
    bot = BotScraper()
    bot.run("https://www.latimes.com/")
