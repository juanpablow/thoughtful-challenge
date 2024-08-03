from BotScraper import BotScraper
from robocorp.tasks import task


@task
def rub_bot():
    bot = BotScraper()
    bot.run("https://www.latimes.com/")
