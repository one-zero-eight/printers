import math
from typing import Literal, assert_never

from aiogram import Bot, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.fsm_data import FSMData
from src.bot.routers.tools import button_text_align_left
from src.bot.shared_messages import MAX_WIDTH_FILLER
from src.config_schema import Printer
from src.modules.printing.entity_models import JobAttributes, JobStateEnum, PrinterStatus


class MenuCallback(CallbackData, prefix="menu"):
    menu: Literal["printer", "copies", "pages", "sides", "layout", "cancel", "confirm"]


class MenuDuringPrintingCallback(CallbackData, prefix="menu_during_printing"):
    menu: Literal["cancel"]
    job_id: int


class PrinterCallback(CallbackData, prefix="printer"):
    cups_name: str


def format_configure_message(
    data: FSMData, status: PrinterStatus | None, status_of_document: str | None = None
) -> tuple[str, InlineKeyboardMarkup]:
    assert "pages" in data
    assert "page_ranges" in data
    assert "number_up" in data
    assert "sides" in data
    assert "copies" in data

    if status_of_document:
        caption = f"{status_of_document}{MAX_WIDTH_FILLER}\n"
    else:
        caption = f"Document is ready to be printed{MAX_WIDTH_FILLER}\n"

    caption += f"Total papers: {
        count_of_papers_to_print(
            pages=data['pages'],
            page_ranges=data['page_ranges'],
            number_up=data['number_up'],
            sides=data['sides'],
            copies=data['copies'],
        )
    }\n"

    caption += html.bold(f"🖨 {format_printer_status(status)}\n")

    layout = {"1": "1x1", "2": "1x2", "4": "2x2", "6": "2x3", "9": "3x3", "16": "4x4"}.get(data["number_up"])
    sides = "One side" if data["sides"] == "one-sided" else "Both sides"
    display_printer = button_text_align_left(f"✏️ {status.printer.display_name if status else '—'}")
    display_copies = button_text_align_left(f"✏️ {data['copies']}")
    display_page_ranges = button_text_align_left(f"✏️ {data['page_ranges'] if data['page_ranges'] else 'all'}")
    display_layout = button_text_align_left(f"✏️ {layout}")
    display_sides = button_text_align_left(f"✏️ {sides}")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Printer", callback_data=MenuCallback(menu="printer").pack()),
                InlineKeyboardButton(text=display_printer, callback_data=MenuCallback(menu="printer").pack()),
            ],
            [
                InlineKeyboardButton(text="Copies", callback_data=MenuCallback(menu="copies").pack()),
                InlineKeyboardButton(text=display_copies, callback_data=MenuCallback(menu="copies").pack()),
            ],
            [
                InlineKeyboardButton(text="Layout", callback_data=MenuCallback(menu="layout").pack()),
                InlineKeyboardButton(text=display_layout, callback_data=MenuCallback(menu="layout").pack()),
            ],
            [
                InlineKeyboardButton(text="Pages", callback_data=MenuCallback(menu="pages").pack()),
                InlineKeyboardButton(text=display_page_ranges, callback_data=MenuCallback(menu="pages").pack()),
            ],
            [
                InlineKeyboardButton(text="Print on", callback_data=MenuCallback(menu="sides").pack()),
                InlineKeyboardButton(text=display_sides, callback_data=MenuCallback(menu="sides").pack()),
            ],
            [
                InlineKeyboardButton(text="✖️ Cancel", callback_data=MenuCallback(menu="cancel").pack()),
                InlineKeyboardButton(text="✅ Confirm", callback_data=MenuCallback(menu="confirm").pack()),
            ],
        ]
    )

    return caption, markup


def format_printer_status(status: PrinterStatus) -> str:
    if not status:
        return "—"
    show_text = f"{status.printer.display_name}"
    if status.offline:
        show_text += ", ☠️ Offline"
    elif status.toner_percentage is not None and status.paper_percentage is not None:
        show_text += f" 🩸 {status.toner_percentage}% 📄 {status.paper_percentage}%"
    elif status.toner_percentage is not None:
        show_text += f" 🩸 {status.toner_percentage}%"
    elif status.paper_percentage is not None:
        show_text += f", 📄 {'is present' if status.paper_percentage > 0 else 'is absent'}"
    return show_text


def format_printing_message(
    data: FSMData,
    printer: Printer | None,
    job_attributes: JobAttributes | None = None,
    iteration: int = 0,
    canceled_manually: bool = False,
    timed_out: bool = False,
) -> str:
    """Format the complete message including job info and status with throbber."""
    assert "pages" in data
    assert "page_ranges" in data
    assert "number_up" in data
    assert "sides" in data
    assert "copies" in data

    LAYOUT = {"1": "1x1", "2": "1x2", "4": "2x2", "6": "2x3", "9": "3x3", "16": "4x4"}.get(data["number_up"], "1x1")

    display_printer = html.bold(html.quote(printer.display_name if printer else "—"))
    display_copies = html.bold(html.quote(str(data["copies"])))
    display_pages_ranges = html.bold(html.quote(data["page_ranges"])) if data["page_ranges"] else html.bold("all")
    display_pages = html.bold(html.quote(str(data["pages"])))
    display_sides = html.bold("One side") if data["sides"] == "one-sided" else html.bold("Two sides")
    display_layout = html.bold(html.quote(LAYOUT))
    caption = (
        html.bold(f"🖨 Printing job:{MAX_WIDTH_FILLER}\n")
        + html.italic(f"⦁ Printer: {display_printer}\n")
        + html.italic(f"⦁ Copies: {display_copies}\n")
        + html.italic(f"⦁ Layout: {display_layout}\n")
        + html.italic(f"⦁ Pages: {display_pages_ranges} (in document: {display_pages})\n")
        + html.italic(f"⦁ Print on: {display_sides}\n")
    )

    max_severity = None
    worst_reason = None
    SEVERITY_ORDER = {"error": 0, "warning": 1, "report": 2}
    printer_state_reasons = job_attributes.printer_state_reasons if job_attributes else []
    for printer_state, severity in printer_state_reasons or []:
        if severity is None:
            continue
        if max_severity is None or SEVERITY_ORDER[severity] < SEVERITY_ORDER[max_severity]:
            max_severity = severity
            worst_reason = printer_state
    if job_attributes:
        if job_attributes.job_state == JobStateEnum.pending:
            throbber = "⏳ Pending"
        elif job_attributes.job_state == JobStateEnum.pending_held:
            throbber = "⏳⏸ Pending held"
        elif job_attributes.job_state == JobStateEnum.processing:
            throbber = "⤹⤿⤻⤺"[iteration % 4] + " Processing"
        elif job_attributes.job_state == JobStateEnum.processing_stopped:
            throbber = "⏸ Paused"
        elif job_attributes.job_state == JobStateEnum.canceled:
            throbber = "❌ Job was cancelled"
        elif job_attributes.job_state == JobStateEnum.aborted:
            throbber = "☠️ Job was aborted"
        elif job_attributes.job_state == JobStateEnum.completed:
            throbber = "✅ Completed"
        else:
            assert_never(job_attributes.job_state)
    else:
        throbber = ""
    caption += f"{throbber}\n"

    notification = None
    if max_severity == "error":
        notification = f"{html.bold('⛔️ Error, requires attention')} ({worst_reason})"
    elif max_severity == "warning":
        notification = f"{html.bold('⚠️ Warning, still printing')} ({worst_reason})"
    elif max_severity == "report":
        notification = f"{html.bold('❕ Report, still printing')} ({worst_reason})"

    if notification is not None:
        if (
            job_attributes
            and job_attributes.printer_state_message
            and not job_attributes.printer_state_message.startswith("Sleep")
        ):
            notification += f":\n{html.italic(job_attributes.printer_state_message)}"
        caption += f"\n{notification}"

    if canceled_manually:
        caption += f"\n{html.bold('Cancelled on demand')}\nPress the button on printer panel if it is still printing."

    if timed_out:
        caption += f"\n{html.bold('Job is timed out ☠️')}\n"

    return caption


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

    cnt = pages
    cnt = math.ceil(cnt / int(number_up))  # CUPS applies number-up to the whole document
    cnt = count_of_pages_to_print(cnt, page_ranges)  # Then CUPS takes page ranges
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


async def discard_job_settings_message(data: FSMData, message: Message, state: FSMContext, bot: Bot):
    if data.get("job_settings_message_id", None):
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=data["job_settings_message_id"])
        except TelegramBadRequest:
            pass
        await state.update_data(job_settings_message_id=None)


async def retrieve_sent_file_properties(message: Message):
    if message.document:
        file_size = message.document.file_size
        file_telegram_identifier = message.document.file_id
        file_telegram_name = message.document.file_name
    else:
        file_size = message.photo[-1].file_size
        file_telegram_identifier = message.photo[-1].file_id
        file_telegram_name = "Photo.png"
    if file_size > 20 * 1024 * 1024:  # 20 MB
        file_size = None
    if not file_telegram_name:
        await message.answer("File name is not supported")
    elif not file_telegram_identifier:
        await message.answer("No file was sent")
    elif not file_size:
        await message.answer(f"File is too large\n\nMaximum size is {html.bold('20 MB')}")
    return file_size, file_telegram_identifier, file_telegram_name
