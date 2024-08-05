import logging


class NoTracebackFormatter(logging.Formatter):
    def formatException(self, exc_info):
        return "%s: %s" % (exc_info[0].__name__, exc_info[1])

    def formatStack(self):
        return ""


logger = logging.getLogger("ROOT")
logger.root.handlers.clear()
logger.root.setLevel(logging.ERROR)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

handler.setFormatter(formatter)
logger.root.addHandler(handler)

verbose_logger = logging.getLogger("BotScrapper")
verbose_logger.propagate = False
verbose_logger.addHandler(handler)
verbose_logger.setLevel(logging.INFO)
