from typing import Literal

from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.api import api_client
from src.bot.routers.printing.printing_tools import discard_job_settings_message
from src.bot.routers.scanning.scanning_states import ScanWork
from src.bot.routers.scanning.scanning_tools import ScanConfigureCallback

router = Router(name="scan_sides_setup")


class ScanSidesCallback(CallbackData, prefix="scan_sides"):
    sides: Literal["false", "true"]


async def start_scan_sides_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.set_state(ScanWork.setup_sides)

    markup = InlineKeyboardBuilder(
        [
            [
                InlineKeyboardButton(text="One side", callback_data=ScanSidesCallback(sides="false").pack()),
                InlineKeyboardButton(text="Both sides", callback_data=ScanSidesCallback(sides="true").pack()),
            ]
        ]
    )
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    msg = await message.answer(
        f"📠 Choose {html.bold('the scanning sides')}",
        reply_markup=markup.as_markup(),
    )
    await state.update_data(job_settings_message_id=msg.message_id)


@router.callback_query(ScanWork.settings_menu, ScanConfigureCallback.filter(F.menu == "sides"))
async def scan_options_sides(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_scan_sides_setup(callback, state, bot)


@router.callback_query(ScanWork.setup_sides, ScanSidesCallback.filter())
async def apply_settings_sides(callback: CallbackQuery, callback_data: ScanSidesCallback, state: FSMContext, bot: Bot):
    from src.bot.routers.scanning.scanning_tools import format_configure_message

    await callback.answer()
    data = await state.update_data(scan_sides=callback_data.sides)
    await discard_job_settings_message(data, callback.message, state, bot)
    await state.set_state(ScanWork.settings_menu)

    assert "confirmation_message_id" in data
    scanner = await api_client.get_scanner(callback.message.chat.id, data.get("scanner"))
    text, markup = format_configure_message(data, scanner)
    await bot.edit_message_text(
        text=text, chat_id=callback.message.chat.id, message_id=data["confirmation_message_id"], reply_markup=markup
    )
