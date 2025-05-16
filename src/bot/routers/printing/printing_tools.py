import math
from collections.abc import Sequence
from typing import Any, assert_never

from aiogram import html
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.config_schema import Printer
from src.modules.printing.entity_models import JobAttributes, JobStateEnum, PrinterStatus


def format_draft_message(
    data: dict[str, Any], status_or_printer: PrinterStatus | Printer | None
) -> tuple[str, InlineKeyboardMarkup]:
    caption = "Document is ready to be printed\n"
    total_papers = count_of_papers_to_print(
        pages=data["pages"],
        page_ranges=data["page_ranges"],
        number_up=data["number_up"],
        sides=data["sides"],
        copies=data["copies"],
    )
    caption += f"Total papers: {total_papers}\n"
    if isinstance(status_or_printer, PrinterStatus):
        status = status_or_printer
        status_or_printer = status.printer
        caption += html.bold(f"🖨 {format_printer_status(status)}\n")
    else:
        caption += f"🖨 {status_or_printer.display_name}\n"

    def empty_inline_space_remainder(string):
        return string + " " * (100 - len(string)) + "."

    layout = {"1": "1x1", "4": "2x2", "9": "3x3"}.get(data["number_up"], None)
    sides = "One side" if data["sides"] == "one-sided" else "Both sides"
    display_printer = empty_inline_space_remainder(f"✏️ {status_or_printer.display_name or "—"}")
    display_copies = empty_inline_space_remainder(f"✏️ {data['copies']}")
    display_page_ranges = empty_inline_space_remainder(
        f"✏️ {'all' if data['page_ranges'] is None else data['page_ranges']}"
    )
    display_layout = empty_inline_space_remainder(f"✏️ {layout}")
    display_sides = empty_inline_space_remainder(f"✏️ {sides}")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Printer", callback_data="Printer"),
                InlineKeyboardButton(text=display_printer, callback_data="Printer"),
            ],
            [
                InlineKeyboardButton(text="Copies", callback_data="Copies"),
                InlineKeyboardButton(text=display_copies, callback_data="Copies"),
            ],
            [
                InlineKeyboardButton(text="Pages", callback_data="Pages"),
                InlineKeyboardButton(text=display_page_ranges, callback_data="Pages"),
            ],
            [
                InlineKeyboardButton(text="Print on", callback_data="Sides"),
                InlineKeyboardButton(text=display_sides, callback_data="Sides"),
            ],
            [
                InlineKeyboardButton(text="Layout", callback_data="Layout"),
                InlineKeyboardButton(text=display_layout, callback_data="Layout"),
            ],
            [
                InlineKeyboardButton(text="✖️ Cancel", callback_data="Cancel"),
                InlineKeyboardButton(text="✅ Confirm", callback_data="Confirm"),
            ],
        ]
    )

    return caption, markup


def format_printing_message(
    data: dict[str, Any],
    printer: Printer | None,
    job_attributes: JobAttributes | None = None,
    iteration: int = 0,
    canceled_manually: bool = False,
    timed_out: bool = False,
) -> str:
    """Format the complete message including job info and status with throbber."""
    LAYOUT = {"1": "1x1", "4": "2x2", "9": "3x3"}.get(data["number_up"], "1x1")

    display_printer = f"{html.bold(html.quote(printer.display_name or "—"))}"
    display_copies = html.bold(html.quote(str(data["copies"])))
    if data["page_ranges"] is None:
        display_pages_ranges = html.bold("all")
    else:
        display_pages_ranges = html.bold(html.quote(data["page_ranges"]))
    display_pages = html.bold(html.quote(str(data["pages"])))
    display_sides = html.bold("One side") if data["sides"] == "one-sided" else html.bold("Two sides")
    display_layout = html.bold(html.quote(LAYOUT))
    job_info = (
        html.italic("Job\n")
        + html.italic(f"⦁ Printer: {display_printer}\n")
        + html.italic(f"⦁ Copies: {display_copies}\n")
        + html.italic(f"⦁ Pages: {display_pages_ranges} (in document: {display_pages})\n")
        + html.italic(f"⦁ Print on: {display_sides}\n")
        + html.italic(f"⦁ Layout: {display_layout}\n")
    )

    max_severity = None
    worst_reason = None
    SEVERITY_ORDER = {
        "error": 0,
        "warning": 1,
        "report": 2,
    }
    for printer_state, severity in job_attributes.printer_state_reasons or []:
        if severity is None:
            continue
        if max_severity is None or SEVERITY_ORDER[severity] < SEVERITY_ORDER[max_severity]:
            max_severity = severity
            worst_reason = printer_state
    if job_attributes:
        if job_attributes.job_state == JobStateEnum.pending:
            throbber = "⏳"
        elif job_attributes.job_state == JobStateEnum.pending_held:
            throbber = "⏳⏸"
        elif job_attributes.job_state == JobStateEnum.processing:
            throbber = "⤹⤿⤻⤺"[iteration % 4]
        elif job_attributes.job_state == JobStateEnum.processing_stopped:
            throbber = "⏸"
        elif job_attributes.job_state == JobStateEnum.canceled:
            throbber = "❌"
        elif job_attributes.job_state == JobStateEnum.aborted:
            throbber = "☠️"
        elif job_attributes.job_state == JobStateEnum.completed:
            throbber = "✅"
        else:
            assert_never(job_attributes.job_state)
    else:
        throbber = ""

    caption = f"{job_info} {throbber}"
    notification = None

    if max_severity == "error":
        notification = f"{html.bold('⛔️ Error, requires attention')} ({worst_reason})"
    elif max_severity == "warning":
        notification = f"{html.bold('⚠️ Warning, still printing')} ({worst_reason})"
    elif max_severity == "report":
        notification = f"{html.bold('❕ Report, still printing')} ({worst_reason})"

    if notification is not None:
        if job_attributes.printer_state_message and not job_attributes.printer_state_message.startswith("Sleep"):
            notification += f":\n{html.italic(job_attributes.printer_state_message)}"
        caption = f"{caption}\n\n{notification}"

    if canceled_manually:
        caption = (
            f"{caption}\n\n{html.bold('Cancelled on demand')}"
            "\nPress the button on printer panel if it is still printing."
        )

    if timed_out:
        caption = f"{caption}\n\n{html.bold('Job is timed out ☠️')}"

    return caption


class PrinterCallback(CallbackData, prefix="printer"):
    cups_name: str


def format_printer_status(status: PrinterStatus) -> str:
    show_text = f"{status.printer.display_name}"
    if status.offline:
        show_text += " ☠️ Offline"
    elif status.toner_percentage is not None and status.paper_percentage is not None:
        show_text += f" 🩸 {status.toner_percentage}% 📄 {status.paper_percentage}%"
    elif status.toner_percentage is not None:
        show_text += f" 🩸 {status.toner_percentage}%"
    elif status.paper_percentage is not None:
        show_text += f" 📄 {status.paper_percentage}%"
    return show_text


def printers_keyboard(printers: Sequence[PrinterStatus | Printer]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for status_or_printer in printers:
        if isinstance(status_or_printer, PrinterStatus):
            printer = status_or_printer.printer
            show_text = format_printer_status(status_or_printer)
        elif isinstance(status_or_printer, Printer):
            printer = status_or_printer
            show_text = printer.display_name
        else:
            assert_never(status_or_printer)
        keyboard.row(
            InlineKeyboardButton(
                text=show_text,
                callback_data=PrinterCallback(cups_name=printer.cups_name).pack(),
            )
        )
    return keyboard.as_markup()


def sub(integers) -> int:
    try:
        return -next(integers) + next(integers) + 1
    except StopIteration:
        return 1


def count_of_papers_to_print(pages: int, page_ranges: str | None, number_up: str, sides: str, copies: str):
    if int(number_up) <= 0:
        raise ValueError("number_up must be positive")
    if pages < 0:
        raise ValueError("pages must be non-negative")

    sides_factor = 1 if sides == "one-sided" else 2

    cnt = count_of_pages_to_print(pages, page_ranges)
    cnt = math.ceil(cnt / int(number_up))
    cnt = math.ceil(cnt / sides_factor)
    cnt *= int(copies)

    return cnt


def count_of_pages_to_print(pages: int, page_ranges: str | None) -> int:
    if pages < 0:
        raise ValueError("pages must be non-negative")

    if page_ranges is None:
        return pages
    if not page_ranges:
        return 0

    total = 0
    for range_str in page_ranges.split(","):
        if "-" in range_str:
            start, end = map(int, range_str.split("-"))
            # Limit range to total pages
            end = min(end, pages)
            if start <= end:
                total += end - start + 1
        else:
            page = int(range_str)
            if 1 <= page <= pages:
                total += 1
    return total


def recalculate_page_ranges(page_range: str, number_up: str) -> str:
    return ",".join(
        map(
            lambda elem: "-".join((str(math.ceil(int(el) / int(number_up)))) for el in elem.split("-")),
            page_range.split(","),
        )
    )
