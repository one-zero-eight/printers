from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)

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
