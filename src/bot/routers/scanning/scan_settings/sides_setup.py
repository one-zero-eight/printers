from typing import Literal

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.api import api_client
from src.bot.routers.scanning.scanning import ScanConfigureCallback
from src.bot.routers.scanning.scanning_states import ScanWork

router = Router(name="scan_sides_setup")


class ScanSidesCallback(CallbackData, prefix="scan_sides"):
    sides: Literal["false", "true"]


async def start_scan_sides_setup(callback_or_message: CallbackQuery | Message, state: FSMContext):
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
    await message.answer(
        f"📠 Choose {html.bold("the scanning sides")}",
        reply_markup=markup.as_markup(),
    )


@router.callback_query(ScanWork.settings_menu, ScanConfigureCallback.filter(F.menu == "sides"))
async def scan_options_sides(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_scan_sides_setup(callback, state)


@router.callback_query(ScanWork.setup_sides, ScanSidesCallback.filter())
async def apply_settings_sides(callback: CallbackQuery, callback_data: ScanSidesCallback, state: FSMContext, bot: Bot):
    from src.bot.routers.scanning.scanning_tools import format_configure_message

    await callback.answer()
    await state.update_data(scan_sides=callback_data.sides)
    await state.set_state(ScanWork.settings_menu)

    data = await state.get_data()
    assert "scan_message_id" in data
    scanner = await api_client.get_scanner(callback.from_user.id, data.get("scanner"))
    text, markup = format_configure_message(data, scanner)
    try:
        await bot.edit_message_text(
            text=text, chat_id=callback.message.chat.id, message_id=data["scan_message_id"], reply_markup=markup
        )
    except TelegramBadRequest:
        pass
    if isinstance(callback.message, Message):
        await callback.message.delete()
