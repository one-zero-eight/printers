from typing import Literal

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import MenuCallback, format_draft_message

router = Router(name="copies_setup")


class SetupCopiesWork(StatesGroup):
    set_copies = State()


class CopiesActionCallback(CallbackData, prefix="copies_action"):
    action: Literal["cancel", "reset"]


@router.callback_query(PrintWork.wait_for_acceptance, MenuCallback.filter(F.menu == "copies"))
async def job_settings_copies(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SetupCopiesWork.set_copies)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✖️ Cancel", callback_data=CopiesActionCallback(action="cancel").pack()),
                InlineKeyboardButton(text="🔄 Reset to 1", callback_data=CopiesActionCallback(action="reset").pack()),
            ]
        ]
    )

    message = await callback.message.answer(
        f"🔢 Send a {html.bold("new amount of copies")}\n\n"
        f"Current value: {html.bold(html.quote((await state.get_data())["copies"]))}\n\n"
        f"Maximum value is {html.bold("50")} (we'll clamp)",
        reply_markup=keyboard,
    )
    await state.update_data(job_settings_copies_message_id=message.message_id)


@router.callback_query(SetupCopiesWork.set_copies, CopiesActionCallback.filter())
async def handle_copies_action(
    callback: CallbackQuery, callback_data: CopiesActionCallback, state: FSMContext, bot: Bot
):
    await callback.answer()

    if callback_data.action == "cancel":
        data = await state.get_data()
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=data["job_settings_copies_message_id"])
        await state.set_state(PrintWork.wait_for_acceptance)
    elif callback_data.action == "reset":
        await state.update_data(copies="1")
        data = await state.get_data()
        printer = await api_client.get_printer(callback.from_user.id, data["printer"])
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
        await state.set_state(PrintWork.wait_for_acceptance)


@router.message(SetupCopiesWork.set_copies)
async def apply_settings_copies(message: Message, state: FSMContext, bot: Bot):
    await message.delete()

    if message.text and message.text.isdigit():
        copies = str(max(0, min(50, int(message.text))))
        await state.update_data(copies=copies)
        data = await state.get_data()
        printer = await api_client.get_printer(message.from_user.id, data["printer"])
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
        await state.set_state(PrintWork.wait_for_acceptance)
    else:
        data = await state.get_data()
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
