import logging


class NoTracebackFormatter(logging.Formatter):
    def formatException(self, exc_info):
        return "%s: %s" % (exc_info[0].__name__, exc_info[1])

    def formatStack(self):
        return ""


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = NoTracebackFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
