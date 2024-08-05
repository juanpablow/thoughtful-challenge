from logger_config import logger

from work_item_loader import WorkItemLoader
from news_scraper import NewsScraper
from excel_saver import ExcelSaver


class BotScraper:
    def __init__(self):
        self.work_item_loader = WorkItemLoader()
        self.news_scraper = None
        self.excel_saver = ExcelSaver()
        logger.info("BotScraper initialized")

    def load_work_item(self):
        self.work_item_loader.load()
        self.news_scraper = NewsScraper(
            self.work_item_loader.search_phrase,
            self.work_item_loader.category,
            self.work_item_loader.months,
        )

    def open_website(self, url):
        self.news_scraper.open_browser()
        self.news_scraper.open_url(url)

    def run(self, url):
        try:
            self.load_work_item()
            self.open_website(url)
            self.news_scraper.search_and_filter_news()
            news = self.news_scraper.get_news()
            self.excel_saver.save(news, self.work_item_loader.search_phrase)
        except Exception as e:
            logger.error(f"An error occurred during execution: {str(e)}")
        finally:
            if self.news_scraper:
                self.news_scraper.driver_quit()


if __name__ == "__main__":
    bot = BotScraper()
    bot.run("https://www.latimes.com/")
