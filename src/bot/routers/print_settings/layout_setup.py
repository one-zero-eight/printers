import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.bot.keyboards import confirmation_keyboard
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import count_of_papers_to_print, update_confirmation_keyboard

router = Router(name="layout_setup")


class SetupLayoutWork(StatesGroup):
    set_layout = State()


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Layout")
async def job_settings_layout(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SetupLayoutWork.set_layout)
    await callback.message.answer(
        f"📖 Set {html.bold("page layout")}\n\n"
        f"This option is about pages per page,\n2x2 will print four pages in one page",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1x1", callback_data="1"),
                    InlineKeyboardButton(text="2x2", callback_data="4"),
                    InlineKeyboardButton(text="3x3", callback_data="9"),
                ]
            ]
        ),
    )


@router.callback_query(SetupLayoutWork.set_layout, lambda callback: callback.data in ["1", "4", "9"])
async def apply_settings_layout(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(number_up=callback.data)
    data = await state.get_data()
    update_confirmation_keyboard(data)
    try:
        await bot.edit_message_caption(
            caption="Document is ready to be printed\n"
            f"Total papers: {count_of_papers_to_print(data["page_ranges"], data["number_up"],
                                                             data["sides"], data["copies"])}\n",
            chat_id=callback.message.chat.id,
            message_id=data["confirmation_message"],
            reply_markup=confirmation_keyboard,
        )
    except aiogram.exceptions.TelegramBadRequest:
        pass
    await callback.message.delete()
    await state.set_state(PrintWork.wait_for_acceptance)
