from aiogram import Bot, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.bot.api import api_client
from src.bot.routers.printing.printing_tools import discard_job_settings_message, format_printing_message


class PrintWork(StatesGroup):
    settings_menu = State()

    setup_copies = State()
    setup_layout = State()
    setup_pages = State()
    setup_printer = State()
    setup_sides = State()

    printing = State()


async def gracefully_interrupt_printing_state(
    callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot
):
    current_state = await state.get_state()
    data = await state.get_data()
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message

    if current_state in (
        PrintWork.settings_menu,
        PrintWork.setup_copies,
        PrintWork.setup_layout,
        PrintWork.setup_pages,
        PrintWork.setup_printer,
        PrintWork.setup_sides,
    ):
        await discard_job_settings_message(data, message, state, bot)
        if "confirmation_message_id" in data:
            try:
                await bot.edit_message_caption(
                    caption=f"{html.bold("You've cancelled this print work 🤷‍♀️")}",
                    chat_id=message.chat.id,
                    message_id=data["confirmation_message_id"],
                )
            except TelegramBadRequest:
                pass
        if "filename" in data:
            await api_client.cancel_not_started_job(callback_or_message.from_user.id, data["filename"])
    elif current_state == PrintWork.printing:
        if "job_id" in data:
            job_attributes = await api_client.check_job(callback_or_message.from_user.id, data["job_id"])
            await api_client.cancel_job(callback_or_message.from_user.id, data["job_id"])
            if "printer" in data and "confirmation_message_id" in data:
                printer = await api_client.get_printer(callback_or_message.from_user.id, data["printer"])
                try:
                    caption = format_printing_message(data, printer, job_attributes, canceled_manually=True)
                    await bot.edit_message_caption(
                        caption=caption, chat_id=message.chat.id, message_id=data["confirmation_message_id"]
                    )
                except TelegramBadRequest:
                    pass
