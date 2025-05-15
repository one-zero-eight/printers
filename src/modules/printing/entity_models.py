from enum import StrEnum
from typing import Literal

from pydantic import Field

from src.config_schema import Printer
from src.logging_ import logger
from src.pydantic_base import BaseSchema


class PrintingOptions(BaseSchema):
    copies: str | None = Field(default=None)
    "Count of copies"
    page_ranges: str | None = Field(default=None, alias="page-ranges")
    "Which page ranges to print"
    sides: Literal["one-sided", "two-sided-long-edge"] | None = Field(default=None)
    "One-sided or double-sided printing"
    number_up: Literal["1", "4", "9"] | None = Field(default=None, alias="number-up")
    "Count of pages on a list"


class JobStateReasonEnum(StrEnum):
    """
    https://www.rfc-editor.org/rfc/rfc8011.html#section-5.3.8
    """

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
    cups_waiting_for_job_completed = "cups-waiting-for-job-completed"
    "CUPS is waiting for the job to complete."
    media_needed = "media-needed"
    "The Printer needs paper loaded."
    toner_low = "toner-low"
    "The Printer is low on toner."
    toner_empty = "toner-empty"
    "The Printer is out of toner."
    media_empty = "media-empty"
    "The Printer is out of paper."
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


class JobAttributes(BaseSchema):
    """
    References:
    - https://www.rfc-editor.org/rfc/rfc8011.html
    - https://github.com/istopwg/pwg-books/blob/master/ippguide/printers.md
    - https://www.iana.org/assignments/ipp-registrations/ipp-registrations.xml
    """

    job_state: JobStateReasonEnum | str
    "The current state of a job from the getJobAttributes function"
    printer_state: (
        list[
            tuple[
                PrinterStateReasonEnum | str,
                Literal["error", "warning", "report", None],
            ]
        ]
        | None
    )
    "The current state of printer: 'cups-waiting-for-job-completed', 'media-needed-warning', 'media-empty-error', 'input-tray-missing', 'media-empty-report'"

    @classmethod
    def parse_job_state(cls, value: str) -> JobStateReasonEnum | str:
        try:
            return JobStateReasonEnum(value)
        except ValueError:
            logger.warning(f"Unknown job state: {value}")
            return value

    @classmethod
    def parse_printer_state(
        cls, value: list[str]
    ) -> list[tuple[PrinterStateReasonEnum | str, Literal["error", "warning", "report", None]]]:
        _result = []
        for v in value:
            if isinstance(v, str):
                try:
                    reason, severity = PrinterStateReasonEnum.from_str(v)
                    _result.append((reason, severity))
                except ValueError:
                    logger.warning(f"Unknown printer state: {v}")
                    _result.append((v, None))
            else:
                logger.warning(f"Unknown printer state: {v}")
                _result.append(v)
        return _result


class PrinterStatus(BaseSchema):
    printer: Printer
    paper_percentage: int | None
    toner_percentage: int | None
