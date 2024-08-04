import logging
from RPA.Robocorp.WorkItems import WorkItems

logger = logging.getLogger(__name__)


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

            self.search_phrase = self._get_mandatory_value(
                work_item_data, "search_phrase"
            )
            self.category = work_item_data.get("category", None)
            self.months = self._get_months(work_item_data)
        except Exception as e:
            logger.error(f"Failed to load work items: {str(e)}")
            raise ValueError(e)

    def _get_mandatory_value(self, data, key):
        try:
            value = data[key]
            if not value:
                raise ValueError(
                    f"The '{key}' is mandatory and was not provided in the work item."
                )
            return value
        except KeyError:
            logger.error(
                f"The '{key}' is mandatory and was not provided in the work item."
            )
            raise ValueError(
                f"The '{key}' is mandatory and was not provided in the work item."
            )

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
