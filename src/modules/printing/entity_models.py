from typing import Literal

from pydantic import BaseModel, Field

from src.config_schema import Printer


class PrintingOptions(BaseModel):
    copies: str | None = None
    "Count of copies"
    page_ranges: str | None = Field(None, alias="page-ranges")
    "Which page ranges to print"
    sides: Literal["one-sided", "two-sided-long-edge"] | None = None
    "One-sided or double-sided printing"
    number_up: Literal["1", "4", "9"] | None = Field(None, alias="number-up")
    "Count of pages on a list"


class JobAttributes(BaseModel):
    job_state: (
        Literal[
            "job-completed-successfully",
            "none",
            "media-empty-report",
            "canceled-at-device",
            "job-printing",
        ]
        | str
    ) = Field(alias="job-state-reasons")
    "The current state of a job from the getJobAttributes function"
    printer_state: list[str] | None = Field(None, alias="job-printer-state-reasons")
    "The current state of printer: 'cups-waiting-for-job-completed', 'media-needed-warning', 'media-empty-error', 'input-tray-missing', 'media-empty-report'"


class PrinterStatus(BaseModel):
    printer: Printer
    total_papers: int | None
    toner_percentage: int | None
