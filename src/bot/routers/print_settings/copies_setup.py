from typing import Literal

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import MenuCallback, format_draft_message

router = Router(name="copies_setup")


class CopiesActionCallback(CallbackData, prefix="copies_action"):
    action: Literal["cancel", "reset"]


async def start_copies_setup(callback_or_message: CallbackQuery | Message, state: FSMContext):
    await state.set_state(PrintWork.setup_copies)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✖️ Cancel", callback_data=CopiesActionCallback(action="cancel").pack()),
                InlineKeyboardButton(text="🔄 Reset to 1", callback_data=CopiesActionCallback(action="reset").pack()),
            ]
        ]
    )
    data = await state.get_data()
    assert "copies" in data

    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    msg = await message.answer(
        f"🔢 Send a {html.bold("new amount of copies")}\n\n"
        f"Current value: {html.bold(html.quote(data["copies"]))}\n\n"
        f"Maximum value is {html.bold("50")} (we'll clamp)",
        reply_markup=keyboard,
    )
    await state.update_data(job_settings_copies_message_id=msg.message_id)


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "copies"))
async def job_settings_copies(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await start_copies_setup(callback, state)


@router.callback_query(PrintWork.setup_copies, CopiesActionCallback.filter())
async def handle_copies_action(
    callback: CallbackQuery, callback_data: CopiesActionCallback, state: FSMContext, bot: Bot
):
    await callback.answer()

    if callback_data.action == "cancel":
        data = await state.get_data()
        assert "job_settings_copies_message_id" in data
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=data["job_settings_copies_message_id"])
        await state.set_state(PrintWork.settings_menu)
    elif callback_data.action == "reset":
        await state.update_data(copies="1")
        data = await state.get_data()
        assert "confirmation_message" in data
        assert "job_settings_copies_message_id" in data
        printer = await api_client.get_printer(callback.from_user.id, data.get("printer"))
        caption, markup = format_draft_message(data, printer)
        try:
            await bot.edit_message_caption(
                caption=caption,
                chat_id=callback.message.chat.id,
                message_id=data["confirmation_message"],
                reply_markup=markup,
            )
        except aiogram.exceptions.TelegramBadRequest:
            pass
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=data["job_settings_copies_message_id"])
        await state.set_state(PrintWork.settings_menu)


@router.message(PrintWork.setup_copies)
async def apply_settings_copies(message: Message, state: FSMContext, bot: Bot):
    await message.delete()

    if message.text and message.text.isdigit():
        copies = str(max(0, min(50, int(message.text))))
        await state.update_data(copies=copies)
        data = await state.get_data()
        assert "confirmation_message" in data
        assert "job_settings_copies_message_id" in data
        printer = await api_client.get_printer(message.from_user.id, data.get("printer"))
        caption, markup = format_draft_message(data, printer)
        try:
            await bot.edit_message_caption(
                caption=caption,
                chat_id=message.chat.id,
                message_id=data["confirmation_message"],
                reply_markup=markup,
            )
        except aiogram.exceptions.TelegramBadRequest:
            pass
        await bot.delete_message(chat_id=message.chat.id, message_id=data["job_settings_copies_message_id"])
        await state.set_state(PrintWork.settings_menu)
    else:
        data = await state.get_data()
        assert "job_settings_copies_message_id" in data
        assert "copies" in data
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=data["job_settings_copies_message_id"],
                text=f"🔢 Incorrect format, we expect a {html.bold("digit")}\n\n"
                f"Current value: {html.bold(html.quote(data["copies"]))}\n\n"
                f"Maximum value is {html.bold("50")} (we'll clamp)",
            )
        except aiogram.exceptions.TelegramBadRequest:
            pass
