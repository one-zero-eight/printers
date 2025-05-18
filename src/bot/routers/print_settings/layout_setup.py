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

router = Router(name="layout_setup")


class LayoutCallback(CallbackData, prefix="layout"):
    number_up: Literal["1", "4", "9"]


async def start_layout_setup(callback_or_message: CallbackQuery | Message, state: FSMContext):
    await state.set_state(PrintWork.setup_layout)
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await message.answer(
        f"📖 Set {html.bold("page layout")}\n\n"
        f"This option is about pages per page,\n2x2 will print four pages in one page",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1x1", callback_data=LayoutCallback(number_up="1").pack()),
                    InlineKeyboardButton(text="2x2", callback_data=LayoutCallback(number_up="4").pack()),
                    InlineKeyboardButton(text="3x3", callback_data=LayoutCallback(number_up="9").pack()),
                ]
            ]
        ),
    )


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "layout"))
async def job_settings_layout(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_layout_setup(callback, state)


@router.callback_query(PrintWork.setup_layout, LayoutCallback.filter())
async def apply_settings_layout(callback: CallbackQuery, callback_data: LayoutCallback, state: FSMContext, bot: Bot):
    await state.update_data(number_up=callback_data.number_up)
    data = await state.get_data()
    assert "confirmation_message" in data
    printer = await api_client.get_printer(callback.from_user.id, data.get("printer"))
    caption, markup = format_draft_message(data, printer)
    try:
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
