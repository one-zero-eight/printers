import asyncio

from aiogram import Bot, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    LoginUrl,
    Message,
    ReplyKeyboardMarkup,
    User,
)

from src.bot.entry_filters import InnohassleUserFilter

router = Router(name="unauthenticated")

I_HAVE_CONNECTED_TELEGRAM = "I have connected telegram to InNoHassle account."


@router.message(~InnohassleUserFilter())
@router.callback_query(~InnohassleUserFilter())
async def any_not_registered_handler(_callback_or_message: CallbackQuery | Message, bot: Bot, event_from_user: User):
    connect_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Connect",
                    login_url=LoginUrl(
                        url="https://innohassle.ru/account/connect-telegram" + f"?bot={(await bot.me()).username}",
                        forward_text="Connect your telegram",
                        bot_username="InNoHassleBot",
                    ),
                )
            ]
        ]
    )
    await bot.send_message(
        event_from_user.id,
        "To continue, you need to connect your Telegram account to the InNoHassle account.",
        reply_markup=connect_kb,
    )
    # wait for the user to connect the account
    await asyncio.sleep(3)
    push_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=I_HAVE_CONNECTED_TELEGRAM)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await bot.send_message(
        event_from_user.id,
        "If you have already connected your account, just press the button or send /start.",
        reply_markup=push_kb,
    )
