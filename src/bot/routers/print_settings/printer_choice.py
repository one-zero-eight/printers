import asyncio

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
)

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import format_draft_message, printers_keyboard
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

    asyncio.create_task(
        update_printer_statuses(
            callback.from_user.id,
            callback.message.chat.id,
            msg.message_id,
            printers,
            state,
            bot,
            checkable_state=SetupPrinterWork.set_printer,
        )
    )


@router.callback_query(
    SetupPrinterWork.set_printer,
    lambda callback: callback.data in map(lambda elem: elem.cups_name, settings.api.printers_list),
)
async def apply_settings_printer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    printer_cups_name = callback.data
    if printer_cups_name is None:
        await callback.answer("Printer not found")
        return
    printer = await api_client.get_printer(callback.from_user.id, printer_cups_name)
    if printer is None:  # Wrong callback.data, no such printer exist now
        await callback.answer("Printer not found")
        return

    await state.update_data(printer=printer.cups_name)
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


async def update_printer_statuses(
    from_user_id: int,
    chat_id: int,
    message_id: int,
    printers: list,
    state: FSMContext,
    bot: Bot,
    checkable_state: State,
):
    tasks = [
        api_client.get_printer_status(from_user_id, printer.cups_name)
        for printer in printers
        if isinstance(printer, Printer)
    ]
    for t in asyncio.as_completed(tasks):
        if await state.get_state() != checkable_state:
            return
        result = await t
        if isinstance(result, PrinterStatus):
            for i, p in enumerate(printers):
                if isinstance(p, Printer) and p.cups_name == result.printer.cups_name:
                    printers[i] = result  # type: ignore

        new_reply_markup = printers_keyboard(printers)
        if await state.get_state() != checkable_state:
            return
        try:
            await bot.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=new_reply_markup,
            )
        except TelegramBadRequest:
            pass
