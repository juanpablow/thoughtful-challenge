from bot_scraper import BotScraper
from robocorp.tasks import task


@task
def run_bot():
    bot = BotScraper()
    bot.run("https://www.latimes.com/")
