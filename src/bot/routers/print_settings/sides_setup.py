from typing import Literal

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import MenuCallback, format_draft_message

router = Router(name="sides_setup")


class SetupSidesWork(StatesGroup):
    set_sides = State()


class SidesCallback(CallbackData, prefix="sides"):
    sides: Literal["one-sided", "two-sided-long-edge"]


@router.callback_query(PrintWork.wait_for_acceptance, MenuCallback.filter(F.menu == "sides"))
async def job_settings_sides(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SetupSidesWork.set_sides)
    await callback.message.answer(
        f"🌚🌝 Set {html.bold("paper sides")}",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="One side", callback_data=SidesCallback(sides="one-sided").pack()),
                    InlineKeyboardButton(
                        text="Both sides", callback_data=SidesCallback(sides="two-sided-long-edge").pack()
                    ),
                ]
            ]
        ),
    )


@router.callback_query(SetupSidesWork.set_sides, SidesCallback.filter())
async def apply_settings_sides(callback: CallbackQuery, callback_data: SidesCallback, state: FSMContext, bot: Bot):
    await state.update_data(sides=callback_data.sides)
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
    if isinstance(callback.message, Message):
        await callback.message.delete()
    await state.set_state(PrintWork.wait_for_acceptance)
