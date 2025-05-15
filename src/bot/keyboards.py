from typing import assert_never

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.config_schema import Printer
from src.modules.printing.entity_models import PrinterStatus

cancel_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="✖️ Cancel", callback_data="Cancel")]]
)

removed_reply_keyboard = ReplyKeyboardRemove(remove_keyboard=True)

confirmation_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Printer", callback_data="Printer"),
            InlineKeyboardButton(text="", callback_data="Printer"),
        ],
        [
            InlineKeyboardButton(text="Copies", callback_data="Copies"),
            InlineKeyboardButton(text="", callback_data="Copies"),
        ],
        [
            InlineKeyboardButton(text="Pages", callback_data="Pages"),
            InlineKeyboardButton(text="", callback_data="Pages"),
        ],
        [
            InlineKeyboardButton(text="Print on", callback_data="Sides"),
            InlineKeyboardButton(text="", callback_data="Sides"),
        ],
        [
            InlineKeyboardButton(text="Layout", callback_data="Layout"),
            InlineKeyboardButton(text="", callback_data="Layout"),
        ],
        [
            InlineKeyboardButton(text="✖️ Cancel", callback_data="Cancel"),
            InlineKeyboardButton(text="✅ Confirm", callback_data="Confirm"),
        ],
    ]
)


def printers_keyboard(printers: list[PrinterStatus | Printer]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for status_or_printer in printers:
        if isinstance(status_or_printer, PrinterStatus):
            printer = status_or_printer.printer
            show_text = printer.name
            if status_or_printer.toner_percentage is not None and status_or_printer.paper_percentage is not None:
                show_text += f" 🩸 {status_or_printer.toner_percentage}% 📄 {status_or_printer.paper_percentage}%"
            elif status_or_printer.toner_percentage is not None:
                show_text += f" 🩸 {status_or_printer.toner_percentage}%"
            elif status_or_printer.paper_percentage is not None:
                show_text += f" 📄 {status_or_printer.paper_percentage}%"
        elif isinstance(status_or_printer, Printer):
            printer = status_or_printer
            show_text = printer.name
        else:
            assert_never(status_or_printer)
        keyboard.row(InlineKeyboardButton(text=show_text, callback_data=printer.name))
    return keyboard.as_markup()
