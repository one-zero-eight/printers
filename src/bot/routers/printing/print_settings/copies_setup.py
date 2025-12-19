from typing import Literal

from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import MenuCallback, discard_job_settings_message, format_draft_message

router = Router(name="copies_setup")


class CopiesActionCallback(CallbackData, prefix="copies_action"):
    action: Literal["cancel", "reset"]


async def start_copies_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
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
        f"🔢 Send a {html.bold('new amount of copies')}\n\n"
        f"Current value: {html.bold(html.quote(data['copies']))}\n\n"
        f"Maximum value is {html.bold('50')} (we'll clamp)",
        reply_markup=keyboard,
    )
    await state.update_data(job_settings_message_id=msg.message_id)


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "copies"))
async def job_settings_copies(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_copies_setup(callback, state, bot)


@router.callback_query(PrintWork.setup_copies, CopiesActionCallback.filter())
async def handle_copies_action(
    callback: CallbackQuery, callback_data: CopiesActionCallback, state: FSMContext, bot: Bot
):
    await callback.answer()
    data = await state.get_data()
    await discard_job_settings_message(data, callback.message, state, bot)
    await state.set_state(PrintWork.settings_menu)
    if callback_data.action == "reset":
        data = await state.update_data(copies="1")
        assert "confirmation_message_id" in data
        printer = await api_client.get_printer(callback.message.chat.id, data.get("printer"))
        caption, markup = format_draft_message(data, printer)
        await bot.edit_message_caption(
            caption=caption,
            chat_id=callback.message.chat.id,
            message_id=data["confirmation_message_id"],
            reply_markup=markup,
        )


@router.message(PrintWork.setup_copies)
async def apply_settings_copies(message: Message, state: FSMContext, bot: Bot):
    await message.delete()

    data = await state.get_data()
    if not message.text or not message.text.isdigit():
        assert "job_settings_message_id" in data
        assert "copies" in data
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data["job_settings_message_id"],
            text=f"🔢 Incorrect format, we expect a {html.bold('digit')}\n\n"
            f"Current value: {html.bold(html.quote(data['copies']))}\n\n"
            f"Maximum value is {html.bold('50')} (we'll clamp)",
        )
        return
    await discard_job_settings_message(data, message, state, bot)
    copies = str(max(0, min(50, int(message.text))))
    data = await state.update_data(copies=copies)
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
