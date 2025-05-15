import asyncio

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
)

from src.bot.api import api_client
from src.bot.keyboards import confirmation_keyboard, printers_keyboard
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import update_confirmation_keyboard
from src.config import settings

router = Router(name="printer_choice")


class SetupPrinterWork(StatesGroup):
    set_printer = State()


@router.callback_query(PrintWork.wait_for_acceptance, F.data == "Printer")
async def job_settings_printer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await state.set_state(SetupPrinterWork.set_printer)
    printers = await api_client.get_printers_list(callback.from_user.id)

    msg = await callback.message.answer(
        f"🖨📠 Choose {html.bold("the printer")}", reply_markup=printers_keyboard(printers)
    )

    async def job():
        printer_statuses = await api_client.get_printers_status_list(callback.from_user.id)
        new_reply_markup = printers_keyboard(printer_statuses)
        try:
            await bot.edit_message_reply_markup(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                reply_markup=new_reply_markup,
            )
        except aiogram.exceptions.TelegramBadRequest:
            pass

    asyncio.create_task(job())


@router.callback_query(
    SetupPrinterWork.set_printer,
    lambda callback: callback.data in map(lambda elem: elem.name, settings.api.printers_list),
)
async def apply_settings_printer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.update_data(printer=callback.data)
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
