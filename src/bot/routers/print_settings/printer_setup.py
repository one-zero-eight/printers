import asyncio
from collections.abc import Sequence
from typing import assert_never

import aiogram.exceptions
from aiogram import Bot, F, Router, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.bot.routers.printing.printing_tools import (
    MenuCallback,
    PrinterCallback,
    format_draft_message,
    format_printer_status,
)
from src.config_schema import Printer
from src.modules.printing.entity_models import PrinterStatus

router = Router(name="printer_choice")


async def start_printer_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.set_state(PrintWork.setup_printer)
    printers = await api_client.get_printers_list(callback_or_message.from_user.id)

    text = f"🖨📠 Choose {html.bold("the printer")}"
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    msg = await message.answer(text, reply_markup=printers_keyboard(printers))

    asyncio.create_task(
        update_printer_statuses(
            callback_or_message.from_user.id,
            message.chat.id,
            msg.message_id,
            printers,
            state,
            bot,
            checkable_state=PrintWork.setup_printer,
        )
    )


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "printer"))
async def job_settings_printer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_printer_setup(callback, state, bot)


@router.callback_query(PrintWork.setup_printer, PrinterCallback.filter())
async def apply_settings_printer(callback: CallbackQuery, callback_data: PrinterCallback, state: FSMContext, bot: Bot):
    printer_cups_name = callback_data.cups_name
    printer = await api_client.get_printer(callback.from_user.id, printer_cups_name)
    if printer is None:  # Wrong callback.data, no such printer exist now
        await callback.answer("Printer not found")
        return

    await state.update_data(printer=printer.cups_name)
    data = await state.get_data()
    assert "printer" in data
    assert "confirmation_message" in data
    printer_status = await api_client.get_printer_status(callback.from_user.id, data.get("printer"))
    try:
        caption, markup = format_draft_message(data, printer_status)
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
    await state.set_state(PrintWork.settings_menu)


def printers_keyboard(printers: Sequence[PrinterStatus | Printer]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    for status_or_printer in printers:
        if isinstance(status_or_printer, PrinterStatus):
            printer = status_or_printer.printer
            show_text = format_printer_status(status_or_printer)
        elif isinstance(status_or_printer, Printer):
            printer = status_or_printer
            show_text = printer.display_name
        else:
            assert_never(status_or_printer)
        keyboard.row(
            InlineKeyboardButton(
                text=show_text,
                callback_data=PrinterCallback(cups_name=printer.cups_name).pack(),
            )
        )
    return keyboard.as_markup()


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
