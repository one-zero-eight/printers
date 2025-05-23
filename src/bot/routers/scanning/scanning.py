import httpx
from aiogram import Bot, F, Router, flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaDocument, Message

from src.bot.api import api_client
from src.bot.interrupts import gracefully_interrupt_state
from src.bot.routers.scanning.scan_settings.mode_setup import start_scan_mode_setup
from src.bot.routers.scanning.scan_settings.scanner_setup import start_scanner_setup
from src.bot.routers.scanning.scanning_states import ScanWork, gracefully_interrupt_scanning_state
from src.bot.routers.scanning.scanning_tools import (
    ScanConfigureCallback,
    ScanningCallback,
    ScanningPausedCallback,
    format_configure_message,
    format_scanning_message,
    format_scanning_paused_message,
)
from src.bot.shared_messages import go_to_default_state
from src.modules.scanning.entity_models import ScanningOptions

router = Router(name="scanning")


@router.message(Command("scan"))
async def command_scan_handler(message: Message, state: FSMContext, bot: Bot):
    await gracefully_interrupt_state(message, state, bot)
    await state.set_state(ScanWork.settings_menu)

    data = await state.get_data()
    data = await state.update_data(
        mode=None if data.get("is_first_time_scan", True) else "manual",
        is_first_time_scan=False,  # Next time we will use "manual" mode by default
        quality="300",
        scan_sides="false",
    )
    assert "mode" in data
    scanner = await api_client.get_scanner(message.from_user.id, data.get("scanner"))
    if scanner:
        data["scanner"] = scanner.name
    else:
        data.pop("scanner", None)

    text, markup = format_configure_message(data, scanner)
    msg = await message.answer(text, reply_markup=markup)
    data["scan_message_id"] = msg.message_id
    await state.update_data(data)

    if data.get("scanner") is None:
        await start_scanner_setup(message, state)
    elif data["mode"] is None:
        await start_scan_mode_setup(message, state)


@router.callback_query(ScanWork.settings_menu, ScanConfigureCallback.filter(F.menu == "cancel"))
async def scan_options_cancel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await gracefully_interrupt_scanning_state(callback, state, bot)
    await go_to_default_state(callback, state)


@router.callback_query(ScanWork.settings_menu, ScanConfigureCallback.filter(F.menu == "start"), StateFilter)
@router.callback_query(ScanWork.pause_menu, ScanningPausedCallback.filter(F.menu == "scan-more"))
@router.callback_query(ScanWork.pause_menu, ScanningPausedCallback.filter(F.menu == "scan-new"))
@flags.chat_action("upload_document")
async def start_scan_handler(
    callback: CallbackQuery, callback_data: ScanConfigureCallback | ScanningPausedCallback, state: FSMContext, bot: Bot
):
    await callback.answer()
    await state.set_state(ScanWork.scanning)

    if isinstance(callback_data, ScanConfigureCallback):  # We are starting a new scan
        data = await state.update_data(scan_filename=None, scan_result_pages_count=None)

    if isinstance(callback_data, ScanningPausedCallback) and callback_data.menu == "scan-new":
        # We are starting a new scan
        data = await state.get_data()
        assert "scan_message_id" in data

        scanner = await api_client.get_scanner(callback.from_user.id, data.get("scanner"))
        try:
            caption, markup = format_scanning_paused_message(data, scanner, is_finished=True)
            await bot.edit_message_caption(
                caption=caption,
                chat_id=callback.message.chat.id,
                message_id=data["scan_message_id"],
                reply_markup=markup,
            )
        except TelegramBadRequest:
            pass

        text, markup = format_scanning_message(data, scanner, "starting")
        msg = await callback.message.answer(text, reply_markup=markup)
        data = await state.update_data(
            scan_message_id=msg.message_id,
            scan_filename=None,
            scan_result_pages_count=None,
        )

    data = await state.get_data()
    assert "scan_message_id" in data
    assert "quality" in data
    assert "mode" in data

    has_caption = data.get("scan_filename") is not None

    scanner = await api_client.get_scanner(callback.from_user.id, data.get("scanner"))
    if not scanner:
        await callback.message.answer("Scanner not found")
        return

    try:
        text, markup = format_scanning_message(data, scanner, "starting")
        if has_caption:
            await bot.edit_message_caption(
                caption=text, chat_id=callback.message.chat.id, message_id=data["scan_message_id"], reply_markup=markup
            )
        else:
            await bot.edit_message_text(
                text=text, chat_id=callback.message.chat.id, message_id=data["scan_message_id"], reply_markup=markup
            )
    except TelegramBadRequest:
        pass

    # Start scanning
    scanning_options = ScanningOptions(
        sides="false" if data["mode"] == "manual" else data.get("scan_sides", "false"),
        quality=data["quality"],
        input_source="Platen" if data["mode"] == "manual" else "Adf",
    )
    try:
        scan_job_id = await api_client.start_manual_scan(callback.from_user.id, scanner, scanning_options)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            await callback.message.answer("Scanner is busy. Try pressing Cancel button on the device and try again.")
            try:
                text, markup = format_scanning_paused_message(data, scanner)
                if has_caption:
                    await bot.edit_message_caption(
                        caption=text,
                        chat_id=callback.message.chat.id,
                        message_id=data["scan_message_id"],
                        reply_markup=markup,
                    )
                else:
                    await bot.edit_message_text(
                        text=text,
                        chat_id=callback.message.chat.id,
                        message_id=data["scan_message_id"],
                        reply_markup=markup,
                    )
            except TelegramBadRequest:
                pass
            await state.set_state(ScanWork.pause_menu)
            return
        raise
    data = await state.update_data(scan_job_id=scan_job_id)
    assert "scan_message_id" in data

    try:
        text, markup = format_scanning_message(data, scanner, "scanning")
        if has_caption:
            await bot.edit_message_caption(
                caption=text, chat_id=callback.message.chat.id, message_id=data["scan_message_id"], reply_markup=markup
            )
        else:
            await bot.edit_message_text(
                text=text, chat_id=callback.message.chat.id, message_id=data["scan_message_id"], reply_markup=markup
            )
    except TelegramBadRequest:
        pass

    # Wait for document to be scanned
    scanning_result = await api_client.wait_and_merge_manual_scan(
        callback.from_user.id, scanner, scan_job_id, data.get("scan_filename")
    )
    data = await state.update_data(
        scan_filename=scanning_result.filename,
        scan_result_pages_count=scanning_result.page_count,
    )
    assert "scan_message_id" in data

    # Update message
    file = await api_client.get_scanned_file(callback.from_user.id, scanning_result.filename)
    input_file = BufferedInputFile(file, filename="scan.pdf")
    text, markup = format_scanning_paused_message(data, scanner)
    await bot.edit_message_media(
        media=InputMediaDocument(media=input_file, caption=text),
        chat_id=callback.message.chat.id,
        message_id=data["scan_message_id"],
        reply_markup=markup,
    )
    await state.set_state(ScanWork.pause_menu)


@router.callback_query(ScanWork.scanning, ScanningCallback.filter(F.menu == "cancel"))
async def scanning_cancel_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await gracefully_interrupt_scanning_state(callback, state, bot)
    await go_to_default_state(callback, state)


@router.callback_query(ScanWork.pause_menu, ScanningPausedCallback.filter(F.menu == "remove-last"))
async def scanning_paused_remove_last_handler(
    callback: CallbackQuery, callback_data: ScanningPausedCallback, state: FSMContext, bot: Bot
):
    await callback.answer()
    await state.set_state(ScanWork.scanning)

    data = await state.get_data()
    assert "scan_message_id" in data

    prev_filename = data.get("scan_filename")
    if not prev_filename:
        await callback.message.answer("No scanned files found")
        return
    scanning_result = await api_client.remove_last_page_manual_scan(callback.from_user.id, prev_filename)
    data = await state.update_data(
        scan_filename=scanning_result.filename,
        scan_result_pages_count=scanning_result.page_count,
    )
    assert "scan_message_id" in data

    # Send file
    file = await api_client.get_scanned_file(callback.from_user.id, scanning_result.filename)
    input_file = BufferedInputFile(file, filename="scan.pdf")
    scanner = await api_client.get_scanner(callback.from_user.id, data.get("scanner"))
    text, markup = format_scanning_paused_message(data, scanner)
    await bot.edit_message_media(
        media=InputMediaDocument(media=input_file, caption=text),
        chat_id=callback.message.chat.id,
        message_id=data["scan_message_id"],
        reply_markup=markup,
    )
    await state.set_state(ScanWork.pause_menu)


@router.callback_query(ScanWork.pause_menu, ScanningPausedCallback.filter(F.menu == "finish"))
async def scanning_paused_finish_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    data = await state.get_data()
    assert "scan_message_id" in data

    scanner = await api_client.get_scanner(callback.from_user.id, data.get("scanner"))
    try:
        caption, markup = format_scanning_paused_message(data, scanner, is_finished=True)
        await bot.edit_message_caption(
            caption=caption, chat_id=callback.message.chat.id, message_id=data["scan_message_id"], reply_markup=markup
        )
    except TelegramBadRequest:
        pass
    await go_to_default_state(callback, state)
