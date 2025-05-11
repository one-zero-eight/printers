import aiogram.exceptions
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
)

from src.bot.keyboards import amount_of_copies_keyboard, confirmation_keyboard
from src.bot.routers.print import PrintWork, update_confirmation_keyboard

router = Router(name="copies_setup")


class SetupJobWork(StatesGroup):
    set_printer = State()
    set_copies = State()
    set_pages = State()
    set_sides = State()
    set_layout = State()


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Copies")
async def job_settings_copies(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SetupJobWork.set_copies)
    await callback.message.answer(
        f"🔢 Modify amount of copies: {(await state.get_data())["copies"]}",
        reply_markup=amount_of_copies_keyboard,
    )


@router.callback_query(SetupJobWork.set_copies, lambda callback: callback.data in "5 -5 1 -1".split())
async def change_settings_copies(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data(copies=str(max(1, int(data["copies"]) + int(callback.data))))
    await callback.message.edit_text(
        text=f"🔢 Modify amount of copies: {(await state.get_data())["copies"]}", reply_markup=amount_of_copies_keyboard
    )


@router.callback_query(SetupJobWork.set_copies, F.data == "Ready")
async def apply_settings_copies(callback: CallbackQuery, state: FSMContext, bot: Bot):
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
