from re import fullmatch

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
)

from src.bot.keyboards import confirmation_keyboard, ready_keyboard
from src.bot.routers.print import PrintWork, update_confirmation_keyboard

router = Router(name="pages_setup")


class SetupJobWork(StatesGroup):
    set_printer = State()
    set_copies = State()
    set_pages = State()
    set_sides = State()
    set_layout = State()


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
    await state.set_state(SetupJobWork.set_pages)
    message = await callback.message.answer(
        text="📑 Send here page ranges to be printed\n\n"
        f"Formatting example: {html.bold("1-5,8,16-20")}\n\n"
        f"Current pages: {html.bold((await state.get_data())["page_ranges"])}",
        reply_markup=ready_keyboard,
    )
    await state.update_data(job_settings_pages_message_id=message.message_id)


def sub(integers: map) -> int:
    return next(integers) - next(integers)


@router.message(SetupJobWork.set_pages)
async def change_settings_pages(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    if (normalized := normalize_page_ranges(message.text)) != message.text:
        await bot.edit_message_text(
            message_id=(await state.get_data())["job_settings_pages_message_id"],
            chat_id=message.chat.id,
            text=html.bold("📑 Incorrect format\n\n") + f"Formatting example: {html.bold("1-5,8,16-20")}\n\n"
            f"Maybe you meant: {html.bold(normalized)}\n\n"
            f"Current pages: {html.bold((await state.get_data())["page_ranges"])}",
            reply_markup=ready_keyboard,
        )
        return
    await state.update_data(page_ranges=normalized)
    await bot.edit_message_text(
        message_id=(await state.get_data())["job_settings_pages_message_id"],
        chat_id=message.chat.id,
        text=html.bold("📑 Set!\n\n") + f"Current pages: {html.bold((await state.get_data())["page_ranges"])}",
        reply_markup=ready_keyboard,
    )


@router.callback_query(SetupJobWork.set_pages, F.data == "Ready")
async def apply_settings_pages(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    update_confirmation_keyboard(data)
    try:
        await bot.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=data["confirmation_message"],
            reply_markup=confirmation_keyboard,
        )
    except aiogram.exceptions.TelegramBadRequest:
        pass
    await callback.message.delete()
    await state.set_state(PrintWork.wait_for_acceptance)
