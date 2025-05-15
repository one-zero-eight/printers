__all__ = ["printing_repository"]


import cups

from src.config import settings
from src.config_schema import Printer
from src.logging_ import logger
from src.modules.printing.entity_models import JobAttributes, PrintingOptions


# noinspection PyMethodMayBeStatic
class PrintingRepository:
    def __init__(self, server: str | None, port: int | None, user: str | None, password: str | None):
        # Settings should be set before calling cups.Connection()
        if server is not None:
            cups.setServer(server)
        if port is not None:
            cups.setPort(port)
        if user is not None:
            cups.setUser(user)
        if password is not None:

            def callback(prompt):
                logger.info(prompt)
                return password

            cups.setPasswordCB(callback)

        self.server = cups.Connection()

    def get_printer(self, name: str) -> Printer | None:
        for elem in settings.api.printers_list:
            if elem.name == name:
                return elem
        return None

    def get_printer_status(self, cups_name: str) -> dict:
        attributes = self.server.getPrinterAttributes(cups_name)
        return attributes

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


printing_repository: PrintingRepository = PrintingRepository(
    settings.api.cups_server,
    settings.api.cups_port,
    settings.api.cups_user,
    settings.api.cups_password,
)
