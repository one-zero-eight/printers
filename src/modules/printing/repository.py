__all__ = ["printing_repository", "PrintingOptions", "JobAttributes"]

from typing import Literal

import cups
from pydantic import BaseModel, Field

from src.config import settings


class PrintingOptions(BaseModel):
    copies: str | None = None
    "Count of copies"
    page_ranges: str | None = Field(None, alias="pages-ranges")
    "Which page ranges to print"
    sides: Literal["one-sided", "two-sided-long-edge"] | None = None
    "One-sided or double-sided printing"
    number_up: Literal["1", "4", "9"] | None = Field(None, alias="number-up")
    "Count of pages on a list"


class JobAttributes(BaseModel):
    job_state: Literal[
        "job-completed-successfully",
        "none",
        "media-empty-report",
        "canceled-at-device",
        "job-canceled-by-user",
        "job-printing",
    ] = Field(alias="job-state-reasons")
    "The current state of a job from the getJobAttributes function"
    printer_state: list[str] | None = Field(None, alias="job-printer-state-reasons")
    "The current state of printer: 'cups-waiting-for-job-completed', 'media-needed-warning', 'media-empty-error', 'input-tray-missing', 'media-empty-report'"


# noinspection PyMethodMayBeStatic
class PrintingRepository:
    def __init__(self):
        cups.setServer(settings.cups_server_host)
        cups.setPort(settings.cups_server_port)
        if settings.cups_server_admin_password:
            cups.setUser(settings.cups_server_admin_user)
            cups.setPasswordCB(lambda: settings.cups_server_admin_password.get_secret_value())
        self.server = cups.Connection(settings.cups_server_host, settings.cups_server_port)

    def print_file(self, printer_name: str, file_name: str, title: str, options: PrintingOptions) -> int:
        options_dict = options.model_dump(by_alias=True, exclude_none=True)
        print(options_dict)
        return self.server.printFile(printer_name, file_name, title, options=options_dict)

    def get_job_status(self, job_id: int) -> JobAttributes:
        attributes = self.server.getJobAttributes(
            job_id, requested_attributes=["job-state-reasons", "job-printer-state-reasons"]
        )
        return JobAttributes.model_validate(attributes)


printing_repository: PrintingRepository = PrintingRepository()
