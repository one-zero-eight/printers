import asyncio
import io
import time

import aiogram.exceptions
import httpx
from aiogram import Bot, F, Router, html
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.bot import shared_messages
from src.bot.api import api_client
from src.bot.keyboards import confirmation_keyboard
from src.bot.logging_ import logger
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import (
    count_of_papers_to_print,
    format_printing_message,
    recalculate_page_ranges,
    update_confirmation_keyboard,
    without_throbber,
)
from src.modules.printing.entity_models import JobStateEnum, PrintingOptions

router = Router(name="printing")


@router.message(PrintWork.request_file, F.document | F.photo)
async def print_work_confirmation(message: Message, state: FSMContext, bot: Bot):
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_DOCUMENT)
    file_telegram_identifier = (
        message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    )
    file_telegram_name = (
        message.document.file_name if message.document else "Photo.png" if message.photo else "Text.txt"
    )
    if not file_telegram_name:
        await message.answer("File name is not supported")
        return
    file = io.BytesIO()
    if file_telegram_identifier:
        await message.bot.download(file=file_telegram_identifier, destination=file)
    else:
        file = io.BytesIO(message.text.encode("utf8"))

    try:
        result = await api_client.prepare_document(message.from_user.id, file_telegram_name, file)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            await message.answer(
                f"Unfortunately, we cannot print this file yet\n"
                f"because of {html.bold(html.quote(e.response.json()["detail"]))}\n\n"
                f"Please, send a file of a supported type:\n"
                f"{html.blockquote(".doc\n.docx\n.png\n.txt\n.jpg\n.md\n.bmp\n.xlsx\n.xls\n.odt\n.ods")}"
            )
            return
        raise

    await state.update_data(pages=result.pages)
    await state.update_data(filename=result.filename)
    data = await state.get_data()
    if "copies" not in data:
        data["copies"] = "1"
    if "page_ranges" not in data:
        data["page_ranges"] = f"1-{result.pages}"
    if "sides" not in data:
        data["sides"] = "one-sided"
    if "number_up" not in data:
        data["number_up"] = "1"
    update_confirmation_keyboard(data)
    document = await api_client.get_prepared_document(message.from_user.id, data["filename"])
    mess = await message.answer_document(
        (
            document := BufferedInputFile(
                document, filename=file_telegram_name[: file_telegram_name.rfind(".")] + ".pdf"
            )
        ),
        caption="Document is ready to be printed\n"
        f"Total papers: {count_of_papers_to_print(data["page_ranges"], data["number_up"],
                                                         data["sides"], data["copies"])}\n",
        reply_markup=confirmation_keyboard,
    )
    data["request_file"] = document
    data["confirmation_message"] = mess.message_id
    await state.update_data(data)
    await state.set_state(PrintWork.wait_for_acceptance)


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Cancel")
async def print_work_preparation_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await api_client.cancel_not_started_job(callback.from_user.id, (await state.get_data())["filename"])
    try:
        if isinstance(callback.message, Message):
            await callback.message.edit_caption(
                caption=f"{without_throbber(callback.message.caption)}"
                f"\n\n{html.bold("You've cancelled this print work 🤷‍♀️")}"
            )
    except aiogram.exceptions.TelegramBadRequest:
        pass
    await shared_messages.send_something(callback, state)


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Confirm")
async def print_work_print(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(PrintWork.printing)
    await bot.send_chat_action(chat_id=callback.message.chat.id, action=ChatAction.UPLOAD_DOCUMENT)

    # Get data and set up printing options
    data = await state.get_data()
    printing_options = PrintingOptions()
    printing_options.copies = data["copies"]
    printing_options.page_ranges = recalculate_page_ranges(data["page_ranges"], data["number_up"])
    printing_options.sides = data["sides"]
    printing_options.number_up = data["number_up"]

    # Start the print job
    job_id = await api_client.begin_job(
        callback.from_user.id,
        data["filename"],
        data["printer"],
        printing_options,
    )

    # Update UI with cancel button
    cancel_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="✖️ Cancel", callback_data=str(job_id))]]
    )
    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(reply_markup=cancel_keyboard)

    # Calculate maximum wait time
    paper_count = count_of_papers_to_print(data["page_ranges"], data["number_up"], data["sides"], data["copies"], False)
    max_sec_per_page = 60
    max_wait_time = max_sec_per_page * paper_count

    # Status monitoring loop
    iteration = 0
    start_time = time.monotonic()

    while time.monotonic() - start_time < max_wait_time:
        iteration += 1
        # Exit if state changed (user clicked cancel)
        if (await state.get_state()) == PrintWork.request_file.state:
            break

        # Get job attributes
        try:
            job_attributes = await api_client.check_job(callback.from_user.id, job_id)
        except httpx.HTTPStatusError as e:
            logger.warning(f"Failed to get job attributes for job {job_id}: {e}")
            await asyncio.sleep(1)
            continue

        # Format message
        caption = format_printing_message(data, job_attributes, iteration)

        # Update message caption with all the information
        try:
            if isinstance(callback.message, Message):
                await callback.message.edit_caption(caption=caption)
        except aiogram.exceptions.TelegramBadRequest:
            pass

        # Handle ended job
        if job_attributes.job_state in [
            JobStateEnum.completed,
            JobStateEnum.canceled,
            JobStateEnum.aborted,
        ]:
            await shared_messages.send_something(callback, state, job_attributes)
            break

        # Sleep for one second before next check
        await asyncio.sleep(1)

    # Handle timeout case
    else:
        try:
            if isinstance(callback.message, Message):
                caption = format_printing_message(data, job_attributes, timed_out=True)
                await callback.message.edit_caption(caption=caption)
        except aiogram.exceptions.TelegramBadRequest:
            pass
        await shared_messages.send_something(callback, state, job_attributes)


@router.callback_query(PrintWork.printing)
async def print_work_cancel(callback: CallbackQuery, state: FSMContext):
    if callback.data is not None:
        job_id = int(callback.data)
        data = await state.get_data()
        job_attributes = await api_client.check_job(callback.from_user.id, job_id)
        await api_client.cancel_job(callback.from_user.id, job_id)
        await shared_messages.send_something(callback, state, job_attributes)

        try:
            caption = format_printing_message(data, job_attributes, canceled_manually=True)
            if isinstance(callback.message, Message):
                await callback.message.edit_caption(caption=caption)
        except (aiogram.exceptions.TelegramBadRequest, KeyError):
            pass
