from logger_config import verbose_logger
from RPA.Excel.Files import Files


class ExcelSaver:
    def __init__(self):
        self.excel = Files()

    def save(self, news, search_phrase):
        try:
            if not news:
                verbose_logger.warning("No news data to save.")
                return
            excel_filename = search_phrase.lower().replace(" ", "-")
            self.excel.create_workbook(f"output/news_{excel_filename}.xlsx")
            self.excel.append_rows_to_worksheet(news, header=True)
            self.excel.save_workbook()
        except Exception as e:
            verbose_logger.error(f"Failed to save news to Excel: {str(e)}")
