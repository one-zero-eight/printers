from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.api import api_client
from src.bot.routers.printing.printing_tools import discard_job_settings_message
from src.bot.routers.scanning.scanning_tools import format_scanning_message, format_scanning_paused_message


class ScanWork(StatesGroup):
    settings_menu = State()

    setup_mode = State()
    setup_quality = State()
    setup_scanner = State()
    setup_sides = State()
    setup_crop = State()
    setup_name = State()

    scanning = State()
    pause_menu = State()


async def gracefully_interrupt_scanning_state(
    callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot
):
    current_state = await state.get_state()
    data = await state.get_data()
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message

    if current_state in (
        ScanWork.settings_menu,
        ScanWork.setup_mode,
        ScanWork.setup_quality,
        ScanWork.setup_scanner,
        ScanWork.setup_sides,
    ):
        await discard_job_settings_message(data, message, state, bot)
        assert "confirmation_message_id" in data
        try:
            await bot.edit_message_text(
                text="Scanning cancelled", chat_id=message.chat.id, message_id=data["confirmation_message_id"]
            )
        except TelegramBadRequest:
            pass
    elif current_state == ScanWork.scanning:
        assert "confirmation_message_id" in data
        scanner = await api_client.get_scanner(message.chat.id, data.get("scanner"))
        if scanner and "scan_job_id" in data:
            await api_client.cancel_manual_scan(message.chat.id, scanner, data["scan_job_id"])
        text, markup = format_scanning_message(data, scanner, "cancelled")
        try:
            await bot.edit_message_text(
                text=text, chat_id=message.chat.id, message_id=data["confirmation_message_id"], reply_markup=markup
            )
        except TelegramBadRequest:
            try:
                await bot.edit_message_caption(
                    caption=text,
                    chat_id=message.chat.id,
                    message_id=data["confirmation_message_id"],
                    reply_markup=markup,
                )
            except TelegramBadRequest:
                pass
    elif current_state == ScanWork.pause_menu:
        assert "confirmation_message_id" in data
        scanner = await api_client.get_scanner(message.chat.id, data.get("scanner"))
        caption, markup = format_scanning_paused_message(data, scanner, is_finished=True)
        try:
            await bot.edit_message_caption(
                caption=caption,
                chat_id=message.chat.id,
                message_id=data["confirmation_message_id"],
                reply_markup=markup,
            )
        except TelegramBadRequest:
            pass
