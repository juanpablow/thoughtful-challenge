import logging


class NoStackTraceFormatter(logging.Formatter):
    def format(self, record):
        record.exc_info = None
        record.stack_info = None
        return super(NoStackTraceFormatter, self).format(record)


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = NoStackTraceFormatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
