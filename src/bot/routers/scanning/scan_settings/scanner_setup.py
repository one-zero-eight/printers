from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.api import api_client
from src.bot.routers.scanning.scan_settings.mode_setup import start_scan_mode_setup
from src.bot.routers.scanning.scanning_states import ScanWork
from src.bot.routers.scanning.scanning_tools import ScanConfigureCallback

router = Router(name="scanner_setup")


async def start_scanner_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.set_state(ScanWork.setup_scanner)

    scanners = await api_client.get_scanners_list(callback_or_message.from_user.id)
    keyboard = InlineKeyboardBuilder()
    for scanner in scanners:
        keyboard.row(
            InlineKeyboardButton(
                text=scanner.display_name, callback_data=ScannerCallback(scanner_name=scanner.name).pack()
            )
        )

    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    msg = await message.answer(f"🖨📠 Choose {html.bold('the scanner')}", reply_markup=keyboard.as_markup())
    await state.update_data(job_settings_message_id=msg.message_id)

    # TODO: show scanner statuses


@router.callback_query(ScanWork.settings_menu, ScanConfigureCallback.filter(F.menu == "scanner"))
async def scan_options_scanner(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_scanner_setup(callback, state, bot)


class ScannerCallback(CallbackData, prefix="scanner"):
    scanner_name: str


@router.callback_query(ScanWork.setup_scanner, ScannerCallback.filter())
async def apply_settings_scanner(callback: CallbackQuery, callback_data: ScannerCallback, state: FSMContext, bot: Bot):
    from src.bot.routers.scanning.scanning_tools import format_configure_message

    await callback.answer()
    scanner = await api_client.get_scanner(callback.from_user.id, callback_data.scanner_name)
    if scanner is None:
        await callback.message.answer("Scanner not found")
        return

    await state.update_data(scanner=scanner.name)

    data = await state.get_data()
    assert "confirmation_message_id" in data
    scanner = await api_client.get_scanner(callback.from_user.id, data.get("scanner"))
    text, markup = format_configure_message(data, scanner)
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=callback.message.chat.id,
            message_id=data["confirmation_message_id"],
            reply_markup=markup if data.get("mode") is not None else None,
        )
    except TelegramBadRequest:
        pass
    if isinstance(callback.message, Message):
        await callback.message.delete()

    if data.get("mode") is not None:
        await state.set_state(ScanWork.settings_menu)
    else:
        # Start mode choice
        await start_scan_mode_setup(callback, state, bot)
