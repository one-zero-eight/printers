from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.config_schema import Printer
from src.logging_ import logger


class PrintingOptions(BaseModel):
    copies: str | None = None
    "Count of copies"
    page_ranges: str | None = Field(default=None, alias="page-ranges")
    "Which page ranges to print"
    sides: Literal["one-sided", "two-sided-long-edge"] | None = None
    "One-sided or double-sided printing"
    number_up: Literal["1", "4", "9"] | None = Field(default=None, alias="number-up")
    "Count of pages on a list"


class JobStateReasonEnum(StrEnum):
    job_completed_successfully = "job-completed-successfully"
    none = "none"
    media_empty_report = "media-empty-report"
    canceled_at_device = "canceled-at-device"
    job_printing = "job-printing"


class PrinterStateReasonEnum(StrEnum):
    """
    https://github.com/istopwg/pwg-books/blob/master/ippguide/printers.md#printer-status-attributes

    The "printer-state-reasons" attribute is a list of keyword strings that provide details about the Printer's state:

    'none': Everything is super, nothing to report.
    'media-needed': The Printer needs paper loaded.
    'toner-low': The Printer is low on toner.
    'toner-empty': The Printer is out of toner.
    'marker-supply-low': The Printer is low on ink.
    'marker-supply-empty': The Printer is out of ink.

    The string may also have a severity suffix ("-error", "-warning", or "-report") to tell the Clients whether the reason affects the printing of a job.
    """

    none = "none"
    "Everything is super, nothing to report."
    media_needed = "media-needed"
    "The Printer needs paper loaded."
    toner_low = "toner-low"
    "The Printer is low on toner."
    toner_empty = "toner-empty"
    "The Printer is out of toner."
    marker_supply_low = "marker-supply-low"
    "The Printer is low on ink."
    marker_supply_empty = "marker-supply-empty"
    "The Printer is out of ink."

    @classmethod
    def from_str(cls, value: str) -> tuple["PrinterStateReasonEnum", Literal["error", "warning", "report"] | None]:
        if value.endswith("-error"):
            return cls(value.removesuffix("-error")), "error"
        elif value.endswith("-warning"):
            return cls(value.removesuffix("-warning")), "warning"
        elif value.endswith("-report"):
            return cls(value.removesuffix("-report")), "report"
        else:
            return cls(value), None


class JobAttributes(BaseModel):
    """
    References:
    - https://github.com/istopwg/pwg-books/blob/master/ippguide/printers.md
    - https://www.iana.org/assignments/ipp-registrations/ipp-registrations.xml#ipp-registrations-4
    """

    job_state: JobStateReasonEnum | str = Field(alias="job-state-reasons")
    "The current state of a job from the getJobAttributes function"
    printer_state: (
        list[
            tuple[
                PrinterStateReasonEnum | str,
                Literal["error", "warning", "report"] | None,
            ]
        ]
        | None
    ) = Field(default=None, alias="job-printer-state-reasons")
    "The current state of printer: 'cups-waiting-for-job-completed', 'media-needed-warning', 'media-empty-error', 'input-tray-missing', 'media-empty-report'"

    @field_validator("job_state", mode="before")
    def validate_job_state(cls, value: str):
        try:
            return JobStateReasonEnum(value)
        except ValueError:
            logger.warning(f"Unknown job state: {value}")
            return value

    @field_validator("printer_state", mode="before")
    def validate_printer_state(cls, value: list[str]):
        _result = []
        for v in value:
            try:
                reason, severity = PrinterStateReasonEnum.from_str(v)
                _result.append((reason, severity))
            except ValueError:
                logger.warning(f"Unknown printer state: {v}")
                _result.append((v, None))
        return _result


class PrinterStatus(BaseModel):
    printer: Printer
    paper_percentage: int | None
    toner_percentage: int | None
