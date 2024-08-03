import logging

from RPA.Robocorp.WorkItems import WorkItems
from selenium.webdriver.common.keys import Keys

from CustomSelenium import CustomSelenium

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BotScraper(CustomSelenium):
    def __init__(self):
        super().__init__()
        self.work_items = WorkItems()
        self.search_phrase = ""
        self.category = ""
        self.months = 0
        self.load_work_item()

    def load_work_item(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        work_items_path = os.path.join(current_dir, "devdata", "work-items.json")
        with open(work_items_path, "r") as f:
            work_item = json.load(f)

        try:
            self.search_phrase = work_item["search_phrase"]
        except KeyError:
            logging.error(
                "The 'search_phrase' is mandatory and was not provided in the work item."
            )
            raise ValueError(
                "The 'search_phrase' is mandatory and was not provided in the work item."
            )

        try:
            self.category = work_item["category"]
        except KeyError:
            logging.warning("The 'category' was not provided in the work item.")
            self.category = None

        try:
            self.months = int(work_item["months"])
            if self.months < 0:
                logging.warning(
                    "The 'months' provided is less than 0. Defaulting to 0."
                )
                self.months = 0
        except (KeyError, ValueError):
            logging.warning(
                "The 'months' was not provided or is not a valid integer in the work item, defaulting to 0."
            )
            self.months = 0
        if self.months == 0:
            self.months = 1

    def open_website(self, url):
        self.open_browser()
        self.open_url(url)

    def run(self, url):
        self.open_website(url)
        self.driver_quit()


if __name__ == "__main__":
    bot = BotScraper()
    bot.run("https://www.latimes.com/")
