import logging


from CustomSelenium import CustomSelenium

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class BotScraper(CustomSelenium):
    def __init__(self):
        super().__init__()

    def open_website(self, url):
        self.open_browser()
        self.open_url(url)

    def run(self, url):
        self.open_website(url)
        self.driver_quit()


if __name__ == "__main__":
    bot = BotScraper()
    bot.run("https://www.latimes.com/")
