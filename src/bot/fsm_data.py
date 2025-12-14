from typing import Literal, TypedDict


class FSMData(TypedDict, total=False):
    # A job
    confirmation_message_id: int

    # Printing
    printer: str
    pages: int
    filename: str
    copies: str
    page_ranges: str | None
    sides: Literal["one-sided", "two-sided-long-edge"]
    number_up: Literal["1", "2", "4", "6", "9", "16"]
    job_id: int

    # Settings
    job_settings_message_id: int

    # Scanning
    mode: Literal["manual", "auto"] | None
    scanner: str
    quality: Literal["200", "300", "400", "600"]
    scan_sides: Literal["false", "true"]
    crop: Literal["false", "true"]
    scan_filename: str | None
    scan_result_pages_count: int | None
    scan_job_id: str
