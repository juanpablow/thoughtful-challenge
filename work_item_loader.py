from logger_config import logger
from RPA.Robocorp.WorkItems import WorkItems


class WorkItemLoader:
    def __init__(self):
        self.work_items = WorkItems()
        self.search_phrase = ""
        self.category = ""
        self.months = 0

    def load(self):
        try:
            self.work_items.get_input_work_item()
            work_item_data = self.work_items.get_work_item_variables()

            self.search_phrase = self._get_search_phrase(work_item_data)
            self.category = self._get_category(work_item_data)
            self.months = self._get_months(work_item_data)
        except Exception as e:
            raise ValueError(e)

    def _get_search_phrase(self, data):
        key = "search_phrase"
        error_message = (
            f"The '{key}' is mandatory and was not provided in the work item."
        )
        try:
            value = data[key]
            if isinstance(value, int):
                value = str(value)
            value = value.strip()
            if not value:
                raise ValueError(error_message)
            return value.strip()
        except Exception as e:
            raise ValueError(e)

    def _get_category(self, data):
        key = "category"
        try:
            value = data.get(key, "")
            if isinstance(value, int):
                value = str(value)
            value = value.strip()
            if not value:
                logger.warning(f"The '{key}' was not provided in the work item.")
                return ""
            return value.capitalize()
        except KeyError:
            logger.warning(f"The '{key}' was not provided in the work item.")
            return ""

    def _get_months(self, data):
        try:
            months = int(data.get("months", 0))
            if months < 0:
                logger.warning("The 'months' provided is less than 0. Defaulting to 1.")
                return 1
            return months if months > 0 else 1
        except ValueError:
            logger.warning(
                "The 'months' is not a valid integer in the work item, defaulting to 1."
            )
            return 1
