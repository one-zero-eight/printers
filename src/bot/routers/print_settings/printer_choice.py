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
from src.bot.routers.registration import RegistrationWork
from src.config import settings
from src.config_schema import Printer
from src.modules.printing.entity_models import PrinterStatus

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
        tasks = [
            api_client.get_printer_status(callback.from_user.id, printer.name)
            for printer in printers
            if isinstance(printer, Printer)
        ]
        for t in asyncio.as_completed(tasks):
            if await state.get_state() != SetupPrinterWork.set_printer:
                return
            result = await t
            if isinstance(result, PrinterStatus):
                for i, p in enumerate(printers):
                    if isinstance(p, Printer) and p.name == result.printer.name:
                        printers[i] = result

            new_reply_markup = printers_keyboard(printers)
            if await state.get_state() != RegistrationWork.printer_is_not_set:
                return
            try:
                await bot.edit_message_reply_markup(
                    chat_id=callback.message.chat.id,
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
