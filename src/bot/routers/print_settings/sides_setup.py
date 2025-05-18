from typing import Literal

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import MenuCallback, format_draft_message

router = Router(name="sides_setup")


class SidesCallback(CallbackData, prefix="sides"):
    sides: Literal["one-sided", "two-sided-long-edge"]


async def start_sides_setup(callback_or_message: CallbackQuery | Message, state: FSMContext):
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await state.set_state(PrintWork.setup_sides)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="One side", callback_data=SidesCallback(sides="one-sided").pack()),
                InlineKeyboardButton(
                    text="Both sides", callback_data=SidesCallback(sides="two-sided-long-edge").pack()
                ),
            ]
        ]
    )
    await message.answer(
        f"🌚🌝 Set {html.bold("paper sides")}",
        reply_markup=markup,
    )


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "sides"))
async def job_settings_sides(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_sides_setup(callback, state)


@router.callback_query(PrintWork.setup_sides, SidesCallback.filter())
async def apply_settings_sides(callback: CallbackQuery, callback_data: SidesCallback, state: FSMContext, bot: Bot):
    await state.update_data(sides=callback_data.sides)
    data = await state.get_data()
    assert "confirmation_message" in data
    printer = await api_client.get_printer(callback.from_user.id, data.get("printer"))
    try:
        caption, markup = format_draft_message(data, printer)
        await bot.edit_message_caption(
            caption=caption,
            chat_id=callback.message.chat.id,
            message_id=data["confirmation_message"],
            reply_markup=markup,
        )
    except aiogram.exceptions.TelegramBadRequest:
        pass
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await state.set_state(PrintWork.settings_menu)
