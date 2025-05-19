from typing import Literal

from aiogram import html
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.fsm_data import FSMData
from src.config_schema import Scanner


class ScanConfigureCallback(CallbackData, prefix="scan_menu"):
    menu: Literal["mode", "scanner", "quality", "sides", "cancel", "start"]


class ScanningCallback(CallbackData, prefix="scanning"):
    menu: Literal["cancel"]


class ScanningPausedCallback(CallbackData, prefix="scanning_paused"):
    menu: Literal["remove-last", "scan-more", "scan-new", "finish"]


def format_configure_message(data: FSMData, scanner: Scanner | None) -> tuple[str, InlineKeyboardMarkup]:
    assert "mode" in data
    assert "quality" in data
    assert "scan_sides" in data

    def empty_inline_space_remainder(string):
        return string + " " * (100 - len(string)) + "."

    display_mode = empty_inline_space_remainder(
        f"✏️ {"Manual Scan" if data["mode"] == "manual" else "Auto Scan" if data["mode"] == "auto" else "—"}"
    )
    display_scanner = empty_inline_space_remainder(f"✏️ {scanner.display_name if scanner else "—"}")
    display_quality = empty_inline_space_remainder(f"✏️ {data['quality']} DPI")
    display_sides = empty_inline_space_remainder(f"✏️ {'One side' if data['scan_sides'] == 'false' else 'Both sides'}")
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

    text = ""
    if data["mode"] == "manual":
        text += (
            html.bold("📠 Manual Scan.\n")
            + "Please place your document on the scanner glass.\n"
            + "You will be able to scan multiple pages one-by-one.\n\n"
        )
    elif data["mode"] == "auto":
        text += (
            html.bold("📠 Auto Scan.\n")
            + "Please place all your papers in the automatic feeder on top of the printer.\n\n"
        )
    else:
        text += html.bold("📠 Scan.\n") + "Not ready. Configure the options first"

    if scanner:
        text += f"🖨 {scanner.display_name}\n"

    return text, markup


def format_scanning_header(data: FSMData, scanner: Scanner | None) -> str:
    assert "mode" in data
    assert "quality" in data
    assert "scan_sides" in data

    display_scanner = html.bold(html.quote(scanner.display_name if scanner else "—"))
    display_quality = html.bold(html.quote(f"{data['quality']} DPI"))
    display_sides = html.bold("One side" if data["scan_sides"] == "false" else "Both sides")

    text = ""
    if data["mode"] == "manual":
        text += html.bold("📠 Manual Scan:\n")
    elif data["mode"] == "auto":
        text += html.bold("📠 Auto Scan:\n")
    else:
        text += html.bold("📠 Scan:\n")
    text += (
        html.italic(f"⦁ Scanner: {display_scanner}\n")
        + html.italic(f"⦁ Quality: {display_quality}\n")
        + (html.italic(f"⦁ Scan from: {display_sides}\n") if data["mode"] == "auto" else "")
    )
    return text


def format_scanning_message(
    data: FSMData, scanner: Scanner | None, status: Literal["starting", "scanning", "cancelled"]
) -> tuple[str, InlineKeyboardMarkup | None]:
    text = format_scanning_header(data, scanner)
    if status == "starting":
        text += html.italic("⏳ Starting...\n")
    elif status == "scanning":
        text += html.italic("⏩ Scanning...\n")
        if data.get("mode") == "auto":
            text += html.italic(
                "Please place all your papers in the automatic feeder on top of the printer before scanning starts.\n"
            )
    elif status == "cancelled":
        text += html.italic("❌ Cancelled\n")

    if status == "cancelled":
        return text, None

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Cancel", callback_data=ScanningCallback(menu="cancel").pack()),
            ]
        ]
    )
    return text, markup


def format_scanning_paused_message(
    data: FSMData, scanner: Scanner | None, is_finished: bool = False
) -> tuple[str, InlineKeyboardMarkup | None]:
    caption = format_scanning_header(data, scanner)
    if is_finished:
        caption += html.italic("✅ Finished")
    else:
        caption += html.italic("✅ Completed")
    caption += " " * 100 + "&#x200D;"

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
                    text="⏩ Scan new document", callback_data=ScanningPausedCallback(menu="scan-new").pack()
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Remove last page", callback_data=ScanningPausedCallback(menu="remove-last").pack()
                ),
                InlineKeyboardButton(text="🏁 Finish", callback_data=ScanningPausedCallback(menu="finish").pack()),
            ],
        ]
    )
    return caption, markup
