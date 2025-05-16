from re import fullmatch

from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
)

from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import (
    format_draft_message,
)

router = Router(name="pages_setup")


class SetupPagesWork(StatesGroup):
    set_pages = State()


def normalize_page_ranges(page_ranges: str) -> str:
    if not fullmatch("([0-9]+[-,])*[0-9]+", page_ranges):
        corrected_ranges = ",".join(
            [
                "-".join(["".join(map(lambda e: e if e.isdigit() else "", el)) for el in elem.split("-") if el])
                for elem in page_ranges.split(",")
                if elem
            ]
        )
        while "--" in corrected_ranges:
            corrected_ranges = corrected_ranges.replace("--", "-")
        if not corrected_ranges:
            raise ValueError("No valid page ranges found")
        if corrected_ranges[0] == "-":
            corrected_ranges = corrected_ranges[1:]
        if corrected_ranges[1] == "-":
            corrected_ranges = corrected_ranges[:-1]
        return (
            ",".join(
                [
                    elem
                    if "-" not in elem
                    else "-".join(elem.split("-")[::-1])
                    if sub(map(int, elem.split("-"))) > 0
                    else elem
                    for elem in corrected_ranges.split(",")
                ]
            )
            if corrected_ranges
            else "1"
        )
    return ",".join(
        [
            elem if "-" not in elem else "-".join(elem.split("-")[::-1]) if sub(map(int, elem.split("-"))) > 0 else elem
            for elem in page_ranges.split(",")
        ]
    )


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Pages")
async def job_settings_pages(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SetupPagesWork.set_pages)
    data = await state.get_data()
    display_current = html.quote(data["page_ranges"]) if data["page_ranges"] else "all"
    message = await callback.message.answer(
        text="📑 Send here page ranges to be printed\n\n"
        f"Formatting example: {html.bold("1-5,8,16-20")}\n\n"
        f"Current pages: {html.bold(display_current)}"
    )
    await state.update_data(job_settings_pages_message_id=message.message_id)


def sub(integers: map) -> int:
    return next(integers) - next(integers)


@router.message(SetupPagesWork.set_pages)
async def change_settings_pages(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    data = await state.get_data()
    if message.text == "all":
        data["page_ranges"] = None
    elif message.text:
        try:
            normalized = normalize_page_ranges(message.text)

            if normalized != message.text:
                display_current = html.quote(data["page_ranges"]) if data["page_ranges"] else "all"
                try:
                    await bot.edit_message_text(
                        message_id=data["job_settings_pages_message_id"],
                        chat_id=message.chat.id,
                        text=html.bold("📑 Incorrect format\n\n")
                        + f"Formatting example: {html.bold("1-5,8,16-20")}\n\n"
                        f"Maybe you meant: {html.bold(html.quote(normalized))}\n\n"
                        f"Current pages: {html.bold(display_current)}",
                    )
                except TelegramBadRequest:
                    pass
                return
            data["page_ranges"] = normalized
        except ValueError:
            display_current = html.quote(data["page_ranges"]) if data["page_ranges"] else "all"
            try:
                await bot.edit_message_text(
                    message_id=data["job_settings_pages_message_id"],
                    chat_id=message.chat.id,
                    text=html.bold("📑 Incorrect format\n\n") + f"Formatting example: {html.bold("1-5,8,16-20")}\n\n"
                    f"Current pages: {html.bold(display_current)}",
                )
            except TelegramBadRequest:
                pass
            return
    await state.update_data(data)

    caption, markup = format_draft_message(data)
    try:
        await bot.edit_message_caption(
            caption=caption,
            chat_id=message.chat.id,
            message_id=data["confirmation_message"],
            reply_markup=markup,
        )
    except TelegramBadRequest:
        pass
    await bot.delete_message(chat_id=message.chat.id, message_id=data["job_settings_pages_message_id"])
    await state.set_state(PrintWork.wait_for_acceptance)
