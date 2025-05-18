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

router = Router(name="scan_quality_setup")


class ScanQualityCallback(CallbackData, prefix="scan_quality"):
    quality: Literal["200", "300", "400", "600"]


async def start_quality_setup(callback_or_message: CallbackQuery | Message, state: FSMContext):
    await state.set_state(ScanWork.setup_quality)

    markup = InlineKeyboardBuilder(
        [
            [
                InlineKeyboardButton(text="200 DPI", callback_data=ScanQualityCallback(quality="200").pack()),
                InlineKeyboardButton(text="300 DPI", callback_data=ScanQualityCallback(quality="300").pack()),
            ],
            [
                InlineKeyboardButton(text="400 DPI", callback_data=ScanQualityCallback(quality="400").pack()),
                InlineKeyboardButton(text="600 DPI", callback_data=ScanQualityCallback(quality="600").pack()),
            ],
        ]
    )
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await message.answer(
        f"🖨📠 Choose {html.bold("the scanning quality")}\n"
        "The higher the quality, the larger the file size and the longer the scan time.\n",
        reply_markup=markup.as_markup(),
    )


@router.callback_query(ScanWork.settings_menu, ScanConfigureCallback.filter(F.menu == "quality"))
async def scan_options_quality(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_quality_setup(callback, state)


@router.callback_query(ScanWork.setup_quality, ScanQualityCallback.filter())
async def apply_settings_quality(
    callback: CallbackQuery, callback_data: ScanQualityCallback, state: FSMContext, bot: Bot
):
    from src.bot.routers.scanning.scanning_tools import format_configure_message

    await callback.answer()
    await state.update_data(quality=callback_data.quality)
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
