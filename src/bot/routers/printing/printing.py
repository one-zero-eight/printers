import asyncio
import io
import time
from typing import Literal

import aiogram.exceptions
import httpx
from aiogram import Bot, F, Router, flags, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    ContentType,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram_media_group import media_group_handler

from src.bot import shared_messages
from src.bot.api import api_client
from src.bot.interrupts import gracefully_interrupt_state
from src.bot.logging_ import logger
from src.bot.routers.print_settings.printer_setup import start_printer_setup
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import (
    MenuCallback,
    count_of_papers_to_print,
    format_draft_message,
    format_printing_message,
)
from src.modules.printing.entity_models import JobStateEnum, PrintingOptions

router = Router(name="printing")


@router.message(F.media_group_id)
@media_group_handler
async def album_handler(messages: list[Message]):
    # restrict any albums
    await messages[-1].answer("Multiple files are not supported yet, send one file at a time")


@router.message(F.document | F.photo)
@flags.chat_action("upload_document")
async def document_handler(message: Message, state: FSMContext, bot: Bot):
    await gracefully_interrupt_state(message, state, bot)

    file_size = (
        message.document.file_size if message.document else message.photo[-1].file_size if message.photo else None
    )
    file_telegram_identifier = (
        message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    )
    file_telegram_name = (
        message.document.file_name if message.document else "Photo.png" if message.photo else "Text.txt"
    )

    if not file_telegram_name:
        await message.answer("File name is not supported")
        return
    if not file_telegram_identifier:
        await message.answer("No file was sent")
        return
    if file_size is None or file_size > 20 * 1024 * 1024:  # 20 MB
        await message.answer(f"File is too large\n\nMaximum size is {html.bold('20 MB')}")
        return

    msg = await message.answer("Downloading...")
    file = io.BytesIO()
    await bot.download(file=file_telegram_identifier, destination=file)

    await msg.edit_text("Converting document to PDF...")
    try:
        result = await api_client.prepare_document(message.from_user.id, file_telegram_name, file)
    except httpx.HTTPStatusError as e:
        await msg.delete()
        if e.response.status_code == 400:
            await message.answer(
                f"Unfortunately, we cannot print this file yet\n"
                f"because of {html.bold(html.quote(e.response.json()['detail']))}\n\n"
                f"Please, send a file of a supported type:\n"
                f"{html.blockquote('.doc\n.docx\n.png\n.txt\n.jpg\n.md\n.bmp\n.xlsx\n.xls\n.odt\n.ods')}\n"
                f"or convert the file to PDF manually and try again."
            )
            return
        if e.response.status_code == 500:
            await message.answer(
                "An error occurred while converting the file.\n"
                "The file may be corrupted or too large,"
                " or the server may be overloaded.\n"
                "Please convert the file to PDF manually and try again."
            )
            return
        raise

    await msg.edit_text("Uploading...")
    data = await state.update_data(
        pages=result.pages,
        filename=result.filename,
        copies="1",
        page_ranges=None,
        sides="one-sided",
        number_up="1",
    )
    assert "filename" in data
    printer = await api_client.get_printer(message.from_user.id, data.get("printer"))
    printer_status = await api_client.get_printer_status(message.from_user.id, printer.cups_name if printer else None)
    caption, markup = format_draft_message(data, printer_status, status_of_document="Uploading...")
    await msg.edit_text(text=caption, reply_markup=markup)
    data["confirmation_message"] = msg.message_id
    await state.update_data(data)
    await state.set_state(PrintWork.settings_menu)

    # Start printer choice if printer is not set
    if data.get("printer") is None:
        await start_printer_setup(message, state, bot)

    # Attach document to the message
    document = await api_client.get_prepared_document(message.from_user.id, data["filename"])
    input_file = BufferedInputFile(document, filename=file_telegram_name[: file_telegram_name.rfind(".")] + ".pdf")
    caption, markup = format_draft_message(data, printer_status)
    await msg.edit_media(aiogram.types.InputMediaDocument(media=input_file, caption=caption), reply_markup=markup)


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "cancel"))
async def cancel_print_configuration_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    assert "filename" in data
    await api_client.cancel_not_started_job(callback.from_user.id, data["filename"])
    try:
        if isinstance(callback.message, Message):
            await callback.message.edit_caption(
                caption=f"{callback.message.caption}\n\n{html.bold("You've cancelled this print work 🤷‍♀️")}"
            )
    except aiogram.exceptions.TelegramBadRequest:
        pass
    await shared_messages.go_to_default_state(callback, state)


class MenuDuringPrintingCallback(CallbackData, prefix="menu_during_printing"):
    menu: Literal["cancel"]
    job_id: int


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "confirm"))
@flags.chat_action("typing")
async def start_print_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(PrintWork.printing)

    # Get data and set up printing options
    data = await state.get_data()
    assert "filename" in data
    assert "printer" in data
    assert "copies" in data
    assert "page_ranges" in data
    assert "number_up" in data
    assert "sides" in data
    assert "pages" in data

    printer = await api_client.get_printer(callback.from_user.id, data["printer"])

    if printer is None:
        await callback.answer("Printer not found")
        return

    printing_options = PrintingOptions(
        copies=data["copies"],
        sides=data["sides"],
    )
    printing_options.page_ranges = data["page_ranges"]
    printing_options.number_up = data["number_up"]

    # Start the print job
    job_id = await api_client.begin_job(
        callback.from_user.id,
        data["filename"],
        printer.cups_name,
        printing_options,
    )
    await state.update_data(job_id=job_id)

    # Update UI with cancel button
    cancel_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✖️ Cancel", callback_data=MenuDuringPrintingCallback(menu="cancel", job_id=job_id).pack()
                )
            ]
        ]
    )
    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=cancel_keyboard)

    # Calculate maximum wait time
    paper_count = count_of_papers_to_print(
        pages=data["pages"],
        page_ranges=data["page_ranges"],
        number_up=data["number_up"],
        sides=data["sides"],
        copies=data["copies"],
    )
    max_sec_per_paper = 60
    max_wait_time = max_sec_per_paper * paper_count

    # Status monitoring loop
    iteration = 0
    start_time = time.monotonic()

    while time.monotonic() - start_time < max_wait_time:
        iteration += 1
        # Exit if state changed (user clicked cancel)
        if (await state.get_state()) == default_state:
            break

        # Get job attributes
        try:
            job_attributes = await api_client.check_job(callback.from_user.id, job_id)
        except httpx.HTTPStatusError as e:
            logger.warning(f"Failed to get job attributes for job {job_id}: {e}")
            await asyncio.sleep(1)
            continue

        # Format message
        caption = format_printing_message(data, printer, job_attributes, iteration)

        is_job_finished = job_attributes.job_state in [
            JobStateEnum.completed,
            JobStateEnum.canceled,
            JobStateEnum.aborted,
        ]

        # Update message caption with all the information
        try:
            if isinstance(callback.message, Message):
                await callback.message.edit_caption(
                    caption=caption, reply_markup=cancel_keyboard if not is_job_finished else None
                )
        except aiogram.exceptions.TelegramBadRequest:
            pass

        # Handle ended job
        if is_job_finished:
            if (await state.get_state()) == PrintWork.printing:
                await shared_messages.go_to_default_state(callback, state)
            break

        # Sleep for one second before next check
        await asyncio.sleep(1)

    # Handle timeout case
    else:
        await api_client.cancel_job(callback.from_user.id, job_id)
        job_attributes = await api_client.check_job(callback.from_user.id, job_id)
        try:
            if isinstance(callback.message, Message):
                caption = format_printing_message(data, printer, job_attributes, timed_out=True)
                await callback.message.edit_caption(caption=caption)
        except aiogram.exceptions.TelegramBadRequest:
            pass
        await shared_messages.go_to_default_state(callback, state)


@router.callback_query(PrintWork.printing, MenuDuringPrintingCallback.filter(F.menu == "cancel"))
async def cancel_print_handler(callback: CallbackQuery, callback_data: MenuDuringPrintingCallback, state: FSMContext):
    job_id = callback_data.job_id
    data = await state.get_data()
    job_attributes = await api_client.check_job(callback.from_user.id, job_id)
    await api_client.cancel_job(callback.from_user.id, job_id)
    await shared_messages.go_to_default_state(callback, state)

    printer = await api_client.get_printer(callback.from_user.id, data.get("printer"))
    try:
        caption = format_printing_message(data, printer, job_attributes, canceled_manually=True)
        if isinstance(callback.message, Message):
            await callback.message.edit_caption(caption=caption)
    except (aiogram.exceptions.TelegramBadRequest, KeyError):
        pass


@router.message(
    F.reply_to_message,
    lambda message: message.reply_to_message.content_type in (ContentType.DOCUMENT, ContentType.PHOTO),
)
async def any_message_handler(message: Message, state: FSMContext, bot: Bot):
    await document_handler(message.reply_to_message, state, bot)
