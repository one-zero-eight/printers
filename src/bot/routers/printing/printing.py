import asyncio
import io
import time
from typing import get_args

import aiogram.exceptions
import httpx
from aiogram import Bot, F, Router, flags, html
from aiogram.filters import StateFilter
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
from src.bot.entry_filters import CallbackFromConfirmationMessageFilter
from src.bot.interrupts import gracefully_interrupt_state
from src.bot.logging_ import logger
from src.bot.routers.printing.print_settings.copies_setup import start_copies_setup
from src.bot.routers.printing.print_settings.layout_setup import start_layout_setup
from src.bot.routers.printing.print_settings.pages_setup import start_pages_setup
from src.bot.routers.printing.print_settings.printer_setup import start_printer_setup
from src.bot.routers.printing.print_settings.sides_setup import start_sides_setup
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import (
    MenuCallback,
    MenuDuringPrintingCallback,
    count_of_papers_to_print,
    discard_job_settings_message,
    format_configure_message,
    format_printing_message,
    retrieve_sent_file_properties,
)
from src.bot.routers.tools import cancel_expiring, ensure_same_structural_message, make_expiring
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

    file_size, file_telegram_identifier, file_telegram_name = await retrieve_sent_file_properties(message)
    if not all([file_size, file_telegram_identifier, file_telegram_name]):
        return

    msg = await message.answer("Downloading...")
    await state.update_data(confirmation_message_id=msg.message_id)
    await state.set_state(PrintWork.settings_menu)
    file = io.BytesIO()
    await bot.download(file=file_telegram_identifier, destination=file)

    await ensure_same_structural_message(msg, "confirmation_message_id", state)
    await msg.edit_text("Converting document to PDF...")
    try:
        result = await api_client.prepare_document(message.chat.id, file_telegram_name, file)
    except httpx.HTTPStatusError as e:
        if e.response.status_code not in (400, 500):
            raise
        await ensure_same_structural_message(msg, "confirmation_message_id", state)
        await msg.edit_text(
            f"Unfortunately, we cannot print this file yet\n"
            f"because of {html.bold(html.quote(e.response.json()['detail']))}\n\n"
            f"Please, send a file of a supported type:\n"
            f"{html.blockquote('.doc\n.docx\n.png\n.txt\n.jpg\n.md\n.bmp\n.xlsx\n.xls\n.odt\n.ods')}\n"
            f"or convert the file to PDF manually and try again."
            if e.response.status_code == 400
            else "An error occurred while converting the file.\n"
            "The file may be corrupted or too large,"
            " or the server may be overloaded.\n"
            "Please convert the file to PDF manually and try again."
        )
        return

    await ensure_same_structural_message(msg, "confirmation_message_id", state)
    await msg.edit_text("Uploading...")
    data = await state.update_data(
        pages=result.pages, filename=result.filename, copies="1", page_ranges=None, sides="one-sided", number_up="1"
    )
    printer = await api_client.get_printer(message.chat.id, data.get("printer"))
    printer_status = await api_client.get_printer_status(message.chat.id, printer.cups_name) if printer else None

    await ensure_same_structural_message(msg, "confirmation_message_id", state)
    caption, markup = format_configure_message(data, printer_status, status_of_document="Uploading...")
    await msg.edit_text(text=caption, reply_markup=markup if data.get("printer") is not None else None)

    # Start printer choice if printer is not set
    if data.get("printer") is None:
        await start_printer_setup(message, state, bot)

    # Attach document to the message
    document = await api_client.get_prepared_document(message.chat.id, data["filename"])
    input_file = BufferedInputFile(document, filename=file_telegram_name[: file_telegram_name.rfind(".")] + ".pdf")
    caption, markup = format_configure_message(data, printer_status)
    await ensure_same_structural_message(msg, "confirmation_message_id", state)
    try:
        msg = await msg.edit_media(
            aiogram.types.InputMediaDocument(media=input_file, caption=caption),
            reply_markup=markup if data.get("printer") is not None else None,
        )
    except Exception as e:
        logger.error(f"Failed to attach the prepared document: {e}", exc_info=True)

    data = await state.get_data()
    caption, markup = format_configure_message(data, printer_status)
    await ensure_same_structural_message(msg, "confirmation_message_id", state)
    await make_expiring(msg)
    await msg.edit_caption(caption=caption, reply_markup=markup if data.get("printer") is not None else None)


@router.callback_query(CallbackFromConfirmationMessageFilter(), MenuCallback.filter(F.menu == "cancel"))
async def cancel_print_configuration_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    data = await state.get_data()
    await discard_job_settings_message(data, callback.message, state, bot)
    assert "filename" in data
    try:
        await api_client.cancel_not_started_job(callback.message.chat.id, data["filename"])
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise e
        logger.warning(f"Failed to find a file to delete: {e}")
    await shared_messages.go_to_default_state(callback, state)
    await callback.message.edit_caption(
        caption=f"{callback.message.caption}\n\n{html.bold("You've cancelled this print work 🤷‍♀️")}"
    )
    await cancel_expiring(callback.message)


@router.callback_query(CallbackFromConfirmationMessageFilter(), MenuCallback.filter(F.menu == "confirm"))
@flags.chat_action("typing")
async def start_print_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await cancel_expiring(callback.message)
    await callback.answer()
    await state.set_state(PrintWork.printing)

    # Get data and set up printing options
    data = await state.get_data()
    await discard_job_settings_message(data, callback.message, state, bot)

    assert "filename" in data
    assert "printer" in data
    assert "copies" in data
    assert "page_ranges" in data
    assert "number_up" in data
    assert "sides" in data
    assert "pages" in data

    printer = await api_client.get_printer(callback.message.chat.id, data["printer"])

    if printer is None:
        await callback.answer("Printer not found")
        return

    printing_options = PrintingOptions()
    printing_options.copies = data["copies"]
    printing_options.sides = data["sides"]
    printing_options.page_ranges = data["page_ranges"]
    printing_options.number_up = data["number_up"]

    # Start the print job
    job_id = await api_client.begin_job(
        callback.message.chat.id,
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
    await callback.message.edit_reply_markup(reply_markup=cancel_keyboard)

    # Calculate maximum wait time
    max_sec_per_paper = 60
    max_wait_time = max_sec_per_paper * count_of_papers_to_print(
        pages=data["pages"],
        page_ranges=data["page_ranges"],
        number_up=data["number_up"],
        sides=data["sides"],
        copies=data["copies"],
    )

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
            job_attributes = await api_client.check_job(callback.message.chat.id, job_id)
        except httpx.HTTPStatusError as e:
            logger.warning(f"Failed to get job attributes for job {job_id}: {e}")
            await asyncio.sleep(1)
            continue

        # Update the message
        caption = format_printing_message(data, printer, job_attributes, iteration)
        is_job_finished = job_attributes.job_state in [
            JobStateEnum.completed,
            JobStateEnum.canceled,
            JobStateEnum.aborted,
        ]
        await callback.message.edit_caption(
            caption=caption, reply_markup=cancel_keyboard if not is_job_finished else None
        )

        # Handle ended job
        if is_job_finished:
            if (await state.get_state()) == PrintWork.printing:
                await shared_messages.go_to_default_state(callback, state)
            break

        # Sleep for one second before next check
        await asyncio.sleep(1)

    # Handle timeout case
    else:
        await api_client.cancel_job(callback.message.chat.id, job_id)
        job_attributes = await api_client.check_job(callback.message.chat.id, job_id)
        caption = format_printing_message(data, printer, job_attributes, timed_out=True)
        await shared_messages.go_to_default_state(callback, state)
        await callback.message.edit_caption(caption=caption)


@router.callback_query(
    CallbackFromConfirmationMessageFilter(), PrintWork.printing, MenuDuringPrintingCallback.filter(F.menu == "cancel")
)
async def cancel_print_handler(callback: CallbackQuery, callback_data: MenuDuringPrintingCallback, state: FSMContext):
    job_id = callback_data.job_id
    data = await state.get_data()
    job_attributes = await api_client.check_job(callback.message.chat.id, job_id)
    await api_client.cancel_job(callback.message.chat.id, job_id)
    await shared_messages.go_to_default_state(callback, state)

    printer = await api_client.get_printer(callback.message.chat.id, data.get("printer"))
    caption = format_printing_message(data, printer, job_attributes, canceled_manually=True)
    await callback.message.edit_caption(caption=caption)


@router.message(
    F.reply_to_message,
    lambda message: message.reply_to_message.content_type in (ContentType.DOCUMENT, ContentType.PHOTO),
)
async def reply_handler(message: Message, state: FSMContext, bot: Bot):
    await document_handler(message.reply_to_message, state, bot)


@router.callback_query(
    ~StateFilter(PrintWork.settings_menu), CallbackFromConfirmationMessageFilter(), MenuCallback.filter()
)
async def switch_settings_option(callback: CallbackQuery, callback_data: MenuCallback, state: FSMContext, bot: Bot):
    await callback.answer()
    await discard_job_settings_message(await state.get_data(), callback.message, state, bot)
    await [start_printer_setup, start_copies_setup, start_pages_setup, start_sides_setup, start_layout_setup][
        get_args(MenuCallback.model_fields["menu"].annotation).index(callback_data.menu)
    ](callback, state, bot)
