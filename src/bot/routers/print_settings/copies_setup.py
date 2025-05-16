import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
)

from src.bot.keyboards import confirmation_keyboard
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import count_of_papers_to_print, update_confirmation_keyboard

router = Router(name="copies_setup")


class SetupCopiesWork(StatesGroup):
    set_copies = State()


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Copies")
async def job_settings_copies(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SetupCopiesWork.set_copies)
    message = await callback.message.answer(
        f"🔢 Send a {html.bold("new amount of copies")}\n\n"
        f"Current value: {html.bold(html.quote((await state.get_data())["copies"]))}\n\n"
        f"Maximum value is {html.bold("50")} (we'll clamp)"
    )
    await state.update_data(job_settings_copies_message_id=message.message_id)


@router.message(SetupCopiesWork.set_copies)
async def apply_settings_copies(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    if message.text and message.text.isdigit():
        await state.update_data(copies=str(max(0, min(50, int(message.text)))))
        data = await state.get_data()
        update_confirmation_keyboard(data)
        try:
            await bot.edit_message_caption(
                caption="Document is ready to be printed\n"
                f"Total papers: {count_of_papers_to_print(data["page_ranges"], data["number_up"],
                                                                 data["sides"], data["copies"])}\n",
                chat_id=message.chat.id,
                message_id=data["confirmation_message"],
                reply_markup=confirmation_keyboard,
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
                f"Current value: {html.bold(html.quote((await state.get_data())["copies"]))}\n\n"
                f"Maximum value is {html.bold("50")} (we'll clamp)",
            )
        except aiogram.exceptions.TelegramBadRequest:
            pass
