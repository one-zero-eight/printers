from typing import Literal

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
from src.bot.routers.printing.printing_tools import MenuCallback, discard_job_settings_message, format_configure_message

router = Router(name="layout_setup")


class LayoutCallback(CallbackData, prefix="layout"):
    number_up: Literal["1", "2", "4", "6", "9", "16"]


async def start_layout_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.set_state(PrintWork.setup_layout)
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    msg = await message.answer(
        f"📖 Set {html.bold('page layout')}\n\n"
        f"This option is about document pages per printed page,\n2x3 will print 6 pages in one page",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1x1", callback_data=LayoutCallback(number_up="1").pack()),
                    InlineKeyboardButton(text="1x2", callback_data=LayoutCallback(number_up="2").pack()),
                ],
                [
                    InlineKeyboardButton(text="2x2", callback_data=LayoutCallback(number_up="4").pack()),
                    InlineKeyboardButton(text="2x3", callback_data=LayoutCallback(number_up="6").pack()),
                ],
                [
                    InlineKeyboardButton(text="3x3", callback_data=LayoutCallback(number_up="9").pack()),
                    InlineKeyboardButton(text="4x4", callback_data=LayoutCallback(number_up="16").pack()),
                ],
            ]
        ),
    )
    await state.update_data(job_settings_message_id=msg.message_id)


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "layout"))
async def job_settings_layout(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_layout_setup(callback, state, bot)


@router.callback_query(PrintWork.setup_layout, LayoutCallback.filter())
async def apply_settings_layout(callback: CallbackQuery, callback_data: LayoutCallback, state: FSMContext, bot: Bot):
    data = await state.update_data(number_up=callback_data.number_up)
    await discard_job_settings_message(data, callback.message, state, bot)
    assert "confirmation_message_id" in data
    printer_status = await api_client.get_printer_status(callback.message.chat.id, data.get("printer"))
    caption, markup = format_configure_message(data, printer_status)
    await state.set_state(PrintWork.settings_menu)
    await bot.edit_message_caption(
        caption=caption,
        chat_id=callback.message.chat.id,
        message_id=data["confirmation_message_id"],
        reply_markup=markup,
    )
