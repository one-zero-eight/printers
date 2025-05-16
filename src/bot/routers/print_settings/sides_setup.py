import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import format_draft_message

router = Router(name="sides_setup")


class SetupSidesWork(StatesGroup):
    set_sides = State()


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Sides")
async def job_settings_sides(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SetupSidesWork.set_sides)
    await callback.message.answer(
        f"🌚🌝 Set {html.bold("paper sides")}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="One side", callback_data="one-sided"),
                    InlineKeyboardButton(text="Both sides", callback_data="two-sided-long-edge"),
                ]
            ]
        ),
    )


@router.callback_query(SetupSidesWork.set_sides, lambda callback: callback.data in ["one-sided", "two-sided-long-edge"])
async def apply_settings_sides(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(sides=callback.data)
    data = await state.get_data()
    caption, markup = format_draft_message(data)
    try:
        await bot.edit_message_caption(
            caption=caption,
            chat_id=callback.message.chat.id,
            message_id=data["confirmation_message"],
            reply_markup=markup,
        )
    except aiogram.exceptions.TelegramBadRequest:
        pass
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await state.set_state(PrintWork.wait_for_acceptance)
