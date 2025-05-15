from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.api import api_client

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


async def printers_keyboard(message: Message | CallbackQuery) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    printer_statuses = await api_client.get_printers_status_list(message.from_user.id)
    for status in printer_statuses:
        printer = status.printer
        keyboard.add(InlineKeyboardButton(text=printer.name, callback_data=printer.name))
    return keyboard.as_markup()
