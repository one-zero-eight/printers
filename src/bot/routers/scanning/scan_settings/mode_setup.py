from typing import Literal

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.api import api_client
from src.bot.routers.scanning.scanning_states import ScanWork
from src.bot.routers.scanning.scanning_tools import ScanConfigureCallback

router = Router(name="scan_mode_setup")


class ScanModeCallback(CallbackData, prefix="scan_mode"):
    mode: Literal["manual", "auto"]


async def start_scan_mode_setup(callback_or_message: CallbackQuery | Message, state: FSMContext):
    await state.set_state(ScanWork.setup_mode)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Manual Scan", callback_data=ScanModeCallback(mode="manual").pack()),
                InlineKeyboardButton(text="Auto Scan", callback_data=ScanModeCallback(mode="auto").pack()),
            ]
        ]
    )
    text = (
        "<b>📠 Choose the scan mode:</b>\n"
        "⦁ <b>Manual Scan mode:</b> Scan one page at a time, placing your document on the scanner glass.\n"
        "⦁ <b>Auto Scan mode:</b> Scan many pages using automatic feeder (on top of the printer). Supports both-sides scan.\n"
    )
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await message.answer(text, reply_markup=markup)


@router.callback_query(ScanWork.settings_menu, ScanConfigureCallback.filter(F.menu == "mode"))
async def scan_options_mode(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_scan_mode_setup(callback, state)


@router.callback_query(ScanWork.setup_mode, ScanModeCallback.filter())
async def apply_settings_mode(callback: CallbackQuery, callback_data: ScanModeCallback, state: FSMContext, bot: Bot):
    from src.bot.routers.scanning.scanning_tools import format_configure_message

    await callback.answer()
    await state.update_data(mode=callback_data.mode)

    if isinstance(callback.message, Message):
        await callback.message.delete()

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

    await state.set_state(ScanWork.settings_menu)
