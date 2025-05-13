import asyncio
import functools
import io
import math
import time
from typing import Any

import aiogram.exceptions
import httpx
from aiogram import Bot, F, Router, html
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.bot.api import api_client
from src.bot.keyboards import confirmation_keyboard
from src.modules.printing.entity_models import PrintingOptions

router = Router(name="print")


class PrintWork(StatesGroup):
    request_file = State()
    wait_for_acceptance = State()
    printing = State()


def update_confirmation_keyboard(data: dict[str, Any]) -> None:
    def empty_inline_space_remainder(string):
        return string + " " * (100 - len(string)) + "."

    layout = {"1": "1x1", "4": "2x2", "9": "3x3"}.get(data["number_up"], None)
    confirmation_keyboard.inline_keyboard[0][1].text = empty_inline_space_remainder(f"✏️ {data["printer"]}")
    confirmation_keyboard.inline_keyboard[1][1].text = empty_inline_space_remainder(f"✏️ {data["copies"]}")
    confirmation_keyboard.inline_keyboard[2][1].text = empty_inline_space_remainder(f"✏️ {data["page_ranges"]}")
    confirmation_keyboard.inline_keyboard[3][1].text = empty_inline_space_remainder(
        f"✏️ {"One side" if data["sides"] == "one-sided" else "Both sides"}"
    )
    confirmation_keyboard.inline_keyboard[4][1].text = empty_inline_space_remainder(f"✏️ {layout}")


def sub(integers: map) -> int:
    try:
        return -next(integers) + next(integers) + 1
    except StopIteration:
        return 1


def total_count_of_pages_to_print(page_ranges: str) -> int:
    return functools.reduce(lambda result, elem: result + sub(map(int, elem.split("-"))), page_ranges.split(","), 0)


def recalculate_page_ranges(page_range: str, number_up: str) -> str:
    return ",".join(
        map(
            lambda elem: "-".join((str(math.ceil(int(el) / int(number_up)))) for el in elem.split("-")),
            page_range.split(","),
        )
    )


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
    file = io.BytesIO()
    if message.document or message.photo:
        await message.bot.download(file=file_telegram_identifier, destination=file)
    else:
        file = io.BytesIO(message.text.encode("utf8"))
    status, detail = await api_client.prepare_document(message.from_user.id, file_telegram_name, file)
    await state.update_data(pages=detail["pages"])
    await state.update_data(filename=detail["filename"])
    if status is None:
        await message.answer(
            f"Unfortunately, we cannot print this file yet\n"
            f"because of {html.bold(detail)}\n\n"
            f"Please, send a file of a supported type:\n"
            f"{html.blockquote(".doc\n.docx\n.png\n.txt\n"
                                                ".jpg\n.md\n.bmp\n.xlsx\n.xls\n.odt\n.ods")}"
        )
        return
    data = await state.get_data()
    if "copies" not in data:
        data["copies"] = "1"
    if "page_ranges" not in data:
        data["page_ranges"] = f"1-{detail["pages"]}"
    if "sides" not in data:
        data["sides"] = "one-sided"
    if "number_up" not in data:
        data["number_up"] = "1"
    update_confirmation_keyboard(data)
    document = await api_client.get_prepared_document(message.from_user.id, data["filename"])
    caption = "Document is ready to be printed\n" f"Total pages: {html.bold(data["pages"])}\n"
    mess = await message.answer_document(
        (
            document := BufferedInputFile(
                document, filename=file_telegram_name[: file_telegram_name.rfind(".")] + ".pdf"
            )
        ),
        caption=caption,
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
    await callback.message.delete_reply_markup()
    await state.set_state(PrintWork.request_file)
    await callback.message.answer(
        "You've cancelled this print work 🤷‍♀️\n\n"
        f"🖨 Now you can start a new by sending something {html.bold("to be printed")}"
    )


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
    await callback.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="✖️ Cancel", callback_data=str(job_id))]]
        )
    )
    max_sec_per_page = 20
    for i in range(
        int(
            max_sec_per_page
            * int(data["copies"])
            * total_count_of_pages_to_print(recalculate_page_ranges(data["page_ranges"], data["number_up"]))
        )
    ):
        if (await state.get_state()) == PrintWork.request_file.state:
            break
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
        }.get(job_state.get("job-state-reasons", "none"), "Unknown error, cancelled")
        layout = {"1": "1x1", "4": "2x2", "9": "3x3"}[data["number_up"]]
        caption = (
            html.italic("Job\n")
            + html.italic(f"⦁ Copies: {html.bold(data["copies"])}\n")
            + html.italic(f"⦁ Pages: {html.bold(data["page_ranges"])} (total {html.bold(data["pages"])})\n")
            + html.italic(
                f"⦁ Print on: {html.bold("One side") if data["sides"] == "one-sided" else html.bold("Two sides")}\n"
            )
            + html.italic(f"⦁ Layout: {html.bold(layout)}\n")
            + html.bold(status_text + (f" {"⤹ ⤿ ⤻ ⤺".split()[i % 4]}" if status_text != "Job is completed!" else ""))
        )
        try:
            if (await state.get_state()) != PrintWork.request_file.state:
                await callback.message.edit_caption(
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[[InlineKeyboardButton(text="✖️ Cancel", callback_data=str(job_id))]]
                    ),
                )
        except aiogram.exceptions.TelegramBadRequest:
            pass
        if job_state["job-state-reasons"] == "job-completed-successfully":
            await callback.message.delete_reply_markup()
            await state.set_state(PrintWork.request_file)
            await callback.message.answer(
                f"🖨 Now you can start a new by sending something " f"{html.bold("to be printed")}"
            )
            break
        if job_state.get("job-state-reasons", "none") in "none media-empty-report canceled-at-device".split():
            await api_client.cancel_job(callback.from_user.id, job_id)
            await callback.message.delete_reply_markup()
            await state.set_state(PrintWork.request_file)
            await callback.message.answer(
                "Job failed ☠️\n\n" f"🖨 Now you can start a new by sending something {html.bold("to be printed")}"
            )
            return
        await_time -= time.time_ns()
        await asyncio.sleep(max(0, 1 + await_time / 10 ** len(str(abs(await_time)))))
    else:
        await callback.message.delete_reply_markup()
        await state.set_state(PrintWork.request_file)
        await callback.message.answer(
            "Job is timed out ☠️\n\n" f"🖨 Now you can start a new by sending something {html.bold("to be printed")}"
        )


@router.callback_query(PrintWork.printing)
async def print_work_cancel(callback: CallbackQuery, state: FSMContext):
    await api_client.cancel_job(callback.from_user.id, int(callback.data))
    data = await state.get_data()
    layout = {"1": "1x1", "4": "2x2", "9": "3x3"}[data["number_up"]]
    caption = (
        html.italic("Job\n")
        + html.italic(f"⦁ Copies: {html.bold(data["copies"])}\n")
        + html.italic(f"⦁ Pages: {html.bold(data["page_ranges"])} (total {html.bold(data["pages"])})\n")
        + html.italic(
            f"⦁ Print on: {html.bold("One side") if data["sides"] == "one-sided" else html.bold("Two sides")}\n"
        )
        + html.italic(f"⦁ Layout: {html.bold(layout)}\n")
        + html.bold("Cancelled on demand\n")
        + f"However, {html.bold("we unable to revoke partially printed jobs")}. You should try this with printer"
    )
    await callback.message.delete_reply_markup()
    await callback.message.edit_caption(caption=caption)
    await state.set_state(PrintWork.request_file)
    await callback.message.answer(
        "You've cancelled this print work 🤷‍♀️\n\n"
        f"🖨 Now you can start a new by sending something {html.bold("to be printed")}"
    )
