from logger_config import verbose_logger

from work_item_loader import WorkItemLoader
from news_scraper import NewsScraper
from excel_saver import ExcelSaver


class BotScraper:
    def __init__(self):
        self.work_item_loader = WorkItemLoader()
        self.news_scraper = None
        self.excel_saver = ExcelSaver()
        verbose_logger.info("BotScraper initialized")

    def load_work_item(self):
        verbose_logger.info("Loading work item...")
        self.work_item_loader.load()
        self.news_scraper = NewsScraper(
            self.work_item_loader.search_phrase,
            self.work_item_loader.category,
            self.work_item_loader.months,
        )
        verbose_logger.info("Work item loaded successfully.")

    def open_website(self, url):
        verbose_logger.info(f"Opening website: {url}")
        self.news_scraper.open_browser()
        self.news_scraper.open_url(url)
        verbose_logger.info(f"Website opened: {url}")

    def run(self, url):
        verbose_logger.info("Starting bot run...")
        try:
            self.load_work_item()
            self.open_website(url)
            self.news_scraper.search_and_filter_news()
            news = self.news_scraper.get_news()
            self.excel_saver.save(news, self.work_item_loader.search_phrase)
            verbose_logger.info("Bot run completed successfully.")
        except Exception as e:
            verbose_logger.error(f"An error occurred during execution: {str(e)}")
        finally:
            if self.news_scraper:
                self.news_scraper.driver_quit()
                verbose_logger.info("Browser closed.")


if __name__ == "__main__":
    bot = BotScraper()
    bot.run("https://www.latimes.com/")
