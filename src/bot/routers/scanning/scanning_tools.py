import asyncio
from typing import Literal

from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.fsm_data import FSMData
from src.bot.shared_messages import MAX_WIDTH_FILLER
from src.config_schema import Scanner

expiration_tasks = set()
message_expiration_time = 5 * 60 * 60


class ScanConfigureCallback(CallbackData, prefix="scan_menu"):
    menu: Literal["mode", "scanner", "quality", "sides", "crop", "cancel", "start"]


class ScanningCallback(CallbackData, prefix="scanning"):
    menu: Literal["cancel"]


class ScanningPausedCallback(CallbackData, prefix="scanning_paused"):
    menu: Literal["remove-last", "scan-more", "scan-new", "finish", "rename"]


def empty_inline_space_remainder(string):
    return string + " " * (100 - len(string)) + "."


def format_configure_message(data: FSMData, scanner: Scanner | None) -> tuple[str, InlineKeyboardMarkup]:
    assert "mode" in data
    assert "quality" in data
    assert "scan_sides" in data
    assert "crop" in data

    display_mode = empty_inline_space_remainder(
        f"✏️ {'Manual Scan' if data['mode'] == 'manual' else 'Auto Scan' if data['mode'] == 'auto' else '—'}"
    )
    display_scanner = empty_inline_space_remainder(f"✏️ {scanner.display_name if scanner else '—'}")
    display_quality = empty_inline_space_remainder(f"✏️ {data['quality']} DPI")
    display_sides = empty_inline_space_remainder(f"✏️ {'One side' if data['scan_sides'] == 'false' else 'Both sides'}")
    display_crop = empty_inline_space_remainder(f"✏️ {'Disabled' if data['crop'] == 'false' else 'Enabled'}")
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
                InlineKeyboardButton(text="Auto-Crop", callback_data=ScanConfigureCallback(menu="crop").pack()),
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

    text = ""
    if data["mode"] == "manual":
        text += (
            html.bold(f"📠 Manual Scan.{MAX_WIDTH_FILLER}\n")
            + "Please place your document on the scanner glass.\n"
            + "You will be able to scan multiple pages one-by-one.\n\n"
        )
    elif data["mode"] == "auto":
        text += (
            html.bold(f"📠 Auto Scan.{MAX_WIDTH_FILLER}\n")
            + "Please place all your papers in the automatic feeder on top of the printer.\n\n"
        )
    else:
        text += html.bold(f"📠 Scan.{MAX_WIDTH_FILLER}\n") + "Not ready. Configure the options first\n\n"

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
    display_pages_count = (
        html.bold(f"{data.get('scan_result_pages_count', '—')}")
        if data.get("scan_result_pages_count") is not None
        else None
    )

    text = ""
    if data["mode"] == "manual":
        text += html.bold(f"📠 Manual Scan:{MAX_WIDTH_FILLER}\n")
    elif data["mode"] == "auto":
        text += html.bold(f"📠 Auto Scan:{MAX_WIDTH_FILLER}\n")
    else:
        text += html.bold(f"📠 Scan:{MAX_WIDTH_FILLER}\n")
    text += (
        html.italic(f"⦁ Scanner: {display_scanner}\n")
        + html.italic(f"⦁ Quality: {display_quality}\n")
        + (html.italic(f"⦁ Scan from: {display_sides}\n") if data["mode"] == "auto" else "")
        + (html.italic(f"⦁ Scanned pages: {display_pages_count}\n") if display_pages_count else "")
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
                    text=empty_inline_space_remainder("🗑️ Remove last page"),
                    callback_data=ScanningPausedCallback(menu="remove-last").pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⏩ Scan new document", callback_data=ScanningPausedCallback(menu="scan-new").pack()
                ),
                InlineKeyboardButton(
                    text=empty_inline_space_remainder("✏️ Rename"),
                    callback_data=ScanningPausedCallback(menu="rename").pack(),
                ),
            ],
            [
                InlineKeyboardButton(text="🏁 Finish", callback_data=ScanningPausedCallback(menu="finish").pack()),
            ],
        ]
    )
    return caption, markup


async def make_expiring(message: Message):
    task = asyncio.create_task(mark_as_expired(message), name=str(message.message_id))
    expiration_tasks.add(task)
    task.add_done_callback(lambda elem: expiration_tasks.remove(elem))


async def cancel_expiring(message: Message):
    for elem in expiration_tasks:
        if elem.get_name() == str(message.message_id):
            elem.cancel()
            return


async def mark_as_expired(message: Message):
    await asyncio.sleep(message_expiration_time)
    try:
        await message.edit_caption(caption=f"{html.italic('This scan job has expired 🕒')}")
    except Exception:
        await message.edit_text(text=f"{html.italic('This scan job has expired 🕒')}")


async def edit_message_text_anyway(message: Message, text: str, reply_markup: InlineKeyboardMarkup | None = None):
    try:
        await message.edit_caption(caption=text, reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            await message.edit_text(text=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            pass
