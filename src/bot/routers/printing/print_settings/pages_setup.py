from re import fullmatch
from typing import Literal

from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import MenuCallback, discard_job_settings_message, format_draft_message

router = Router(name="pages_setup")


class PagesActionCallback(CallbackData, prefix="pages_action"):
    action: Literal["cancel", "reset"]


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


async def start_pages_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.set_state(PrintWork.setup_pages)
    data = await state.get_data()
    display_current = html.quote(data.get("page_ranges") or "all")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✖️ Cancel", callback_data=PagesActionCallback(action="cancel").pack()),
                InlineKeyboardButton(text="🔄 Reset to all", callback_data=PagesActionCallback(action="reset").pack()),
            ]
        ]
    )

    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    msg = await message.answer(
        text="📑 Send here page ranges to be printed\n\n"
        f"Formatting example: {html.bold('1-5,8,16-20')}\n\n"
        f"Current pages: {html.bold(display_current)}",
        reply_markup=keyboard,
    )
    await state.update_data(job_settings_message_id=msg.message_id)


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "pages"))
async def job_settings_pages(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_pages_setup(callback, state, bot)


def sub(integers: map) -> int:
    return next(integers) - next(integers)


@router.callback_query(PrintWork.setup_pages, PagesActionCallback.filter())
async def handle_pages_action(callback: CallbackQuery, callback_data: PagesActionCallback, state: FSMContext, bot: Bot):
    await callback.answer()

    data = await state.get_data()
    await discard_job_settings_message(data, callback.message, state, bot)
    await state.set_state(PrintWork.settings_menu)
    if callback_data.action == "reset":
        data = await state.update_data(page_ranges=None)
        assert "confirmation_message_id" in data
        printer = await api_client.get_printer(callback.message.chat.id, data.get("printer"))
        caption, markup = format_draft_message(data, printer)
        await bot.edit_message_caption(
            caption=caption,
            chat_id=callback.message.chat.id,
            message_id=data["confirmation_message_id"],
            reply_markup=markup,
        )


@router.message(PrintWork.setup_pages)
async def change_settings_pages(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    data = await state.get_data()
    if message.text == "all":
        data["page_ranges"] = None
    elif message.text:
        assert "job_settings_message_id" in data
        try:
            normalized = normalize_page_ranges(message.text)

            if normalized != message.text:
                display_current = html.quote(data.get("page_ranges") or "all")
                await bot.edit_message_text(
                    message_id=data["job_settings_message_id"],
                    chat_id=message.chat.id,
                    text=html.bold("📑 Incorrect format\n\n") + f"Formatting example: {html.bold('1-5,8,16-20')}\n\n"
                    f"Maybe you meant: {html.bold(html.quote(normalized))}\n\n"
                    f"Current pages: {html.bold(display_current)}",
                )
                return
            data["page_ranges"] = normalized
        except ValueError:
            display_current = html.quote(data.get("page_ranges") or "all")
            await bot.edit_message_text(
                message_id=data["job_settings_message_id"],
                chat_id=message.chat.id,
                text=html.bold("📑 Incorrect format\n\n") + f"Formatting example: {html.bold('1-5,8,16-20')}\n\n"
                f"Current pages: {html.bold(display_current)}",
            )
            return
    await discard_job_settings_message(data, message, state, bot)
    data = await state.update_data(data)
    assert "confirmation_message_id" in data
    printer = await api_client.get_printer(message.chat.id, data.get("printer"))
    caption, markup = format_draft_message(data, printer)
    await state.set_state(PrintWork.settings_menu)
    await bot.edit_message_caption(
        caption=caption,
        chat_id=message.chat.id,
        message_id=data["confirmation_message_id"],
        reply_markup=markup,
    )
