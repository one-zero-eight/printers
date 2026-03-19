from typing import Literal

from aiogram import html
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.fsm_data import FSMData
from src.bot.routers.tools import button_text_align_left
from src.bot.shared_messages import MAX_WIDTH_FILLER
from src.modules.scanning.entity_models import ScannerStatus


class ScanConfigureCallback(CallbackData, prefix="scan_menu"):
    menu: Literal["mode", "scanner", "quality", "sides", "crop", "cancel", "start"]


class ScanningPausedCallback(CallbackData, prefix="scanning_paused"):
    menu: Literal["remove-last", "scan-more", "scan-new", "finish", "rename"]


class ScannerCallback(CallbackData, prefix="scanner"):
    name: str


def format_configure_message(data: FSMData, scanner_status: ScannerStatus | None) -> tuple[str, InlineKeyboardMarkup]:
    assert "mode" in data
    assert "quality" in data
    assert "scan_sides" in data
    assert "crop" in data

    if not data["mode"]:
        text = html.bold(f"Scan.{MAX_WIDTH_FILLER}\n") + "Not ready. Configure the options first\n\n"
    else:
        text = html.bold(f"{data['mode'].capitalize()} Scan.{MAX_WIDTH_FILLER}\n")
        text += (
            "Please place your document on the scanner glass.\n"
            if "Manual" in text
            else "Please place all your papers in the automatic feeder on top of the printer.\n"
        )
        text += "You will be able to scan multiple pages one-by-one.\n\n"

    text += "📠 " + html.bold(format_scanner_name(scanner_status))

    display_mode = button_text_align_left(f"✏️ {f'{data["mode"].capitalize()} Scan' if data['mode'] else '—'}")
    display_scanner = button_text_align_left(f"✏️ {format_scanner_name(scanner_status, False)}")
    display_quality = button_text_align_left(f"✏️ {data['quality']} DPI")
    display_sides = button_text_align_left(f"✏️ {'One side' if data['scan_sides'] == 'false' else 'Both sides'}")
    display_crop = button_text_align_left(f"✏️ {'Disabled' if data['crop'] == 'false' else 'Enabled'}")
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Scanner", callback_data=ScanConfigureCallback(menu="scanner").pack()),
                InlineKeyboardButton(text=display_scanner, callback_data=ScanConfigureCallback(menu="scanner").pack()),
            ],
            [
                InlineKeyboardButton(text="Mode", callback_data=ScanConfigureCallback(menu="mode").pack()),
                InlineKeyboardButton(text=display_mode, callback_data=ScanConfigureCallback(menu="mode").pack()),
            ],
            [
                InlineKeyboardButton(text="Quality", callback_data=ScanConfigureCallback(menu="quality").pack()),
                InlineKeyboardButton(text=display_quality, callback_data=ScanConfigureCallback(menu="quality").pack()),
            ],
            [
                InlineKeyboardButton(text="Auto Crop", callback_data=ScanConfigureCallback(menu="crop").pack()),
                InlineKeyboardButton(text=display_crop, callback_data=ScanConfigureCallback(menu="crop").pack()),
            ],
            [
                InlineKeyboardButton(text="Scan from", callback_data=ScanConfigureCallback(menu="sides").pack()),
                InlineKeyboardButton(text=display_sides, callback_data=ScanConfigureCallback(menu="sides").pack()),
            ]
            if data["mode"] == "auto"
            else [],
            [
                InlineKeyboardButton(text="✖️ Cancel", callback_data=ScanConfigureCallback(menu="cancel").pack()),
                InlineKeyboardButton(text="⏩ Scan", callback_data=ScanConfigureCallback(menu="start").pack()),
            ],
        ]
    )

    return text, markup


def format_scanner_name(status: ScannerStatus | None, decorated_with_status=True) -> str:
    if not status:
        return "—"
    show_text = f"{status.scanner.display_name}"
    if not decorated_with_status:
        return show_text
    return show_text + f", {'☠️ offline' if status.offline else '✔️ online'}"


def format_scanning_message(
    data: FSMData,
    scanner_status: ScannerStatus | None,
    status: Literal["starting", "scanning", "cancelled"],
    iteration: int = 0,
) -> str:
    text = scan_job_summary(data, scanner_status)
    if status == "starting":
        text += html.italic("⏳ Starting...\n")
    elif status == "scanning":
        text += html.italic(f"{'⤹⤿⤻⤺'[iteration % 4]} Scanning...\n")
    elif status == "cancelled":
        text += html.italic("❌ Cancelled\n")
        return text

    return text


def scan_job_summary(data: FSMData, scanner_status: ScannerStatus | None) -> str:
    display_scanner = html.bold(html.quote(format_scanner_name(scanner_status, False)))
    display_quality = html.bold(html.quote(f"{data['quality']} DPI"))
    display_sides = html.bold("One side" if data["scan_sides"] == "false" else "Both sides")
    display_crop = html.bold("Disabled" if data["crop"] == "false" else "Enabled")
    display_pages_count = html.bold(f"{data.get('scan_result_pages_count', '—')}")

    return html.bold(f"📠 {data['mode'].capitalize()} Scan:{MAX_WIDTH_FILLER}\n") + html.italic(
        f"⦁ Scanner: {display_scanner}\n"
        f"⦁ Quality: {display_quality}\n"
        f"{f'⦁ Scan from: {display_sides}\n' if data['mode'] == 'auto' else ''}"
        f"⦁ Auto Crop: {display_crop}\n"
        f"⦁ Scanned pages: {display_pages_count}\n"
    )


def format_scanning_paused_message(
    data: FSMData, scanner_status: ScannerStatus | None, is_finished: bool = False
) -> tuple[str, InlineKeyboardMarkup | None]:
    caption = scan_job_summary(data, scanner_status)
    if is_finished:
        caption += html.italic("✅ Finished\n")
    else:
        caption += html.italic("✅ Completed\n")

    if is_finished:
        return caption, None

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="▶️ Scan one more page" if data.get("mode", "manual") == "manual" else "▶️ Scan more pages",
                    callback_data=ScanningPausedCallback(menu="scan-more").pack(),
                ),
                InlineKeyboardButton(
                    text=button_text_align_left("🗑️ Remove last page"),
                    callback_data=ScanningPausedCallback(menu="remove-last").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏩ Scan new document", callback_data=ScanningPausedCallback(menu="scan-new").pack()
                ),
                InlineKeyboardButton(
                    text=button_text_align_left("✏️ Rename"),
                    callback_data=ScanningPausedCallback(menu="rename").pack(),
                ),
            ],
            [
                InlineKeyboardButton(text="🏁 Finish", callback_data=ScanningPausedCallback(menu="finish").pack()),
            ],
        ]
    )
    return caption, markup
