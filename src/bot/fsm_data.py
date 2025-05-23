from typing import Literal, TypedDict


class FSMData(TypedDict, total=False):
    # Printing
    printer: str
    pages: int
    filename: str
    copies: str
    page_ranges: str | None
    sides: Literal["one-sided", "two-sided-long-edge"]
    number_up: Literal["1", "2", "4", "6", "9", "16"]
    confirmation_message: int
    job_id: int

    # Printing settings
    job_settings_copies_message_id: int
    job_settings_pages_message_id: int

    # Scanning
    is_first_time_scan: bool
    mode: Literal["manual", "auto"] | None
    scanner: str
    quality: Literal["200", "300", "400", "600"]
    scan_sides: Literal["false", "true"]
    scan_message_id: int
    scan_filename: str | None
    scan_result_pages_count: int | None
    scan_job_id: str
