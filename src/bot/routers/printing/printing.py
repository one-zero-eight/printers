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
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import (
    count_of_papers_to_print,
    recalculate_page_ranges,
    update_confirmation_keyboard,
    without_throbber,
)
from src.modules.printing.entity_models import PrintingOptions

router = Router(name="printing")


@router.message(PrintWork.request_file)
async def print_work_confirmation(message: Message, state: FSMContext, bot: Bot):
    if not any((message.document, message.photo, message.text)):
        await message.answer("Only documents, photos, and text messages are supported to be printed")
        return
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
                f"because of {html.bold(e.response.json()["detail"])}\n\n"
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
    data = await state.get_data()
    printing_options = PrintingOptions()
    printing_options.copies = data["copies"]
    printing_options.page_ranges = recalculate_page_ranges(data["page_ranges"], data["number_up"])
    printing_options.sides = data["sides"]
    printing_options.number_up = data["number_up"]
    job_id = await api_client.begin_job(
        callback.from_user.id,
        data["filename"],
        data["printer"],
        printing_options,
    )
    if isinstance(callback.message, Message):
        await callback.message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="✖️ Cancel", callback_data=str(job_id))]]
            )
        )
    caption = ""
    max_sec_per_page = 60
    for i in range(
        max_sec_per_page
        * count_of_papers_to_print(data["page_ranges"], data["number_up"], data["sides"], data["copies"], False)
    ):
        await_time = time.time_ns()
        try:
            job_state = await api_client.check_job(callback.from_user.id, job_id)
        except httpx.HTTPStatusError:
            return
        status_text = {
            "job-completed-successfully": "Job is completed!",
            "none": "Where is no job",
            "media-empty-report": "Media is empty!",
            "canceled-at-device": "The job was cancelled at the printer",
            "job-printing": "Printing",
        }.get(job_state.job_state, f"Unknown error {html.italic(job_state.job_state)}, cancelled")
        layout = {"1": "1x1", "4": "2x2", "9": "3x3"}[data["number_up"]]
        caption = (
            html.italic("Job\n")
            + html.italic(f"⦁ Printer: {html.bold(data["printer"])}\n")
            + html.italic(f"⦁ Copies: {html.bold(data["copies"])}\n")
            + html.italic(f"⦁ Pages: {html.bold(data["page_ranges"])} (in document: {html.bold(data["pages"])})\n")
            + html.italic(
                f"⦁ Print on: {html.bold("One side") if data["sides"] == "one-sided" else html.bold("Two sides")}\n"
            )
            + html.italic(f"⦁ Layout: {html.bold(layout)}\n")
            + f"{html.italic("Status:")} {html.bold(f"{status_text} {"⤹⤿⤻⤺"[i % 4]}")}"
        )
        if (await state.get_state()) == PrintWork.request_file.state:
            break
        try:
            if isinstance(callback.message, Message):   
                await callback.message.edit_caption(
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(text="✖️ Cancel", callback_data=str(job_id))]]
                    ),
                )
        except aiogram.exceptions.TelegramBadRequest:
            pass
        if job_state.job_state == "job-completed-successfully":
            try:
                if isinstance(callback.message, Message):
                    await callback.message.edit_caption(caption=without_throbber(caption))
            except aiogram.exceptions.TelegramBadRequest:
                pass
            await shared_messages.send_something(callback, state)
            break
        if job_state.job_state in ["none", "media-empty-report", "canceled-at-device"]:
            await api_client.cancel_job(callback.from_user.id, job_id)
            try:
                if isinstance(callback.message, Message):
                    await callback.message.edit_caption(
                        caption=f"{without_throbber(caption)}\n\n{html.bold("Job failed ☠️")}"
                    )
            except aiogram.exceptions.TelegramBadRequest:
                pass
            await shared_messages.send_something(callback, state)
            return
        await_time -= time.time_ns()
        await asyncio.sleep(max(0, 1 + await_time / 10 ** len(str(abs(await_time)))))
    else:
        try:
            if isinstance(callback.message, Message):
                await callback.message.edit_caption(
                    caption=f"{without_throbber(caption)}" f"\n\n{html.bold("Job is timed out ☠️")}"
                )
        except aiogram.exceptions.TelegramBadRequest:
            pass
        await shared_messages.send_something(callback, state)


@router.callback_query(PrintWork.printing)
async def print_work_cancel(callback: CallbackQuery, state: FSMContext):
    await shared_messages.send_something(callback, state)
    await api_client.cancel_job(callback.from_user.id, int(callback.data))
    try:
        if isinstance(callback.message, Message):
            await callback.message.edit_caption(
                caption=f"{without_throbber(callback.message.caption)}"
                f"\n\n{html.bold("Cancelled on demand")}"
                "\nHowever, we unable to revoke partially printed jobs."
                f"\nYou should try this with printer"
            )
    except aiogram.exceptions.TelegramBadRequest:
        pass
