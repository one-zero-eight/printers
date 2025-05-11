__all__ = ["printing_repository"]


import cups

from src.config import settings
from src.config_schema import Printer
from src.modules.printing.entity_models import JobAttributes, PrintingOptions


# noinspection PyMethodMayBeStatic
class PrintingRepository:
    def __init__(self):
        self.server = cups.Connection()

    def get_printer(self, name: str) -> Printer | None:
        for elem in settings.api.printers_list:
            if elem.name == name:
                return elem

    def print_file(self, printer: Printer, file_name: str, title: str, options: PrintingOptions) -> int:
        options_dict = options.model_dump(by_alias=True, exclude_none=True)
        return self.server.printFile(printer.cups_name, file_name, title, options=options_dict)

    def get_job_status(self, job_id: int) -> JobAttributes:
        attributes = self.server.getJobAttributes(
            job_id, requested_attributes=["job-state-reasons", "job-printer-state-reasons"]
        )
        return JobAttributes.model_validate(attributes)

    def cancel_job(self, job_id: int):
        self.server.cancelJob(job_id, True)


printing_repository: PrintingRepository = PrintingRepository()
