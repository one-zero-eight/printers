import asyncio
from typing import assert_never

from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
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
    discard_job_settings_message,
    format_configure_message,
    format_printer_status,
)
from src.bot.routers.tools import ensure_same_structural_message
from src.config_schema import Printer
from src.modules.printing.entity_models import PrinterStatus

router = Router(name="printer_choice")


async def start_printer_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.set_state(PrintWork.setup_printer)

    text = f"🖨📠 Choose {html.bold('the printer')}"
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    printers = await api_client.get_printers_list(message.chat.id)
    msg = await message.answer(text, reply_markup=printers_keyboard(printers))
    await state.update_data(job_settings_message_id=msg.message_id)

    asyncio.create_task(
        update_printer_statuses(
            msg,
            printers,
            state,
        )
    )


async def update_printer_statuses(job_settings_message: Message, printers: list[Printer], state: FSMContext):
    printers_or_statuses = dict()
    for elem in printers:
        printers_or_statuses[elem.cups_name] = elem
    tasks = [api_client.get_printer_status(job_settings_message.chat.id, printer.cups_name) for printer in printers]
    for task in asyncio.as_completed(tasks):
        await ensure_same_structural_message(job_settings_message, "job_settings_message_id", state)
        status = await task
        printers_or_statuses[status.printer.cups_name] = status
        new_reply_markup = printers_keyboard(list(printers_or_statuses.values()))
        await ensure_same_structural_message(job_settings_message, "job_settings_message_id", state)
        await job_settings_message.edit_reply_markup(reply_markup=new_reply_markup)


def printers_keyboard(statuses_and_printers: list[PrinterStatus | Printer]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for status_or_printer in statuses_and_printers:
        if isinstance(status_or_printer, PrinterStatus):
            button = InlineKeyboardButton(
                text=format_printer_status(status_or_printer),
                callback_data=PrinterCallback(cups_name=status_or_printer.printer.cups_name).pack(),
            )
        elif isinstance(status_or_printer, Printer):
            button = InlineKeyboardButton(
                text=status_or_printer.display_name,
                callback_data=PrinterCallback(cups_name=status_or_printer.cups_name).pack(),
            )
        else:
            assert_never(status_or_printer)
        keyboard.row(button)
    return keyboard.as_markup()


@router.callback_query(PrintWork.settings_menu, MenuCallback.filter(F.menu == "printer"))
async def job_settings_printer(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_printer_setup(callback, state, bot)


@router.callback_query(PrintWork.setup_printer, PrinterCallback.filter())
async def apply_settings_printer(callback: CallbackQuery, callback_data: PrinterCallback, state: FSMContext, bot: Bot):
    printer_cups_name = callback_data.cups_name
    printer = await api_client.get_printer(callback.message.chat.id, printer_cups_name)
    data = await state.get_data()
    await discard_job_settings_message(data, callback.message, state, bot)
    if printer is None:  # Wrong callback.data, no such printer exist now
        await callback.answer("Printer not found")
        return
    data = await state.update_data(printer=printer.cups_name)
    assert "printer" in data
    assert "confirmation_message_id" in data
    printer_status = await api_client.get_printer_status(callback.message.chat.id, data.get("printer"))
    caption, markup = format_configure_message(data, printer_status)
    await state.set_state(PrintWork.settings_menu)
    await bot.edit_message_caption(
        caption=caption,
        chat_id=callback.message.chat.id,
        message_id=data["confirmation_message_id"],
        reply_markup=markup,
    )
