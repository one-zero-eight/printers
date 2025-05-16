import asyncio

from aiogram import Bot, F, Router, html, types
from aiogram.filters import Command
from aiogram.filters.logic import or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    Message,
)

from src.bot import shared_messages
from src.bot.api import api_client
from src.bot.entry_filters import InnohassleUserFilter
from src.bot.routers.print_settings.printer_choice import update_printer_statuses
from src.bot.routers.printing.printing_tools import PrinterCallback, printers_keyboard

router = Router(name="registration")


class RegistrationWork(StatesGroup):
    printer_is_not_set = State()
    wait_for_connect = State()


I_HAVE_CONNECTED_TELEGRAM = "I have connected telegram to InNoHassle account."


@router.message(
    or_f(Command("start"), F.text == I_HAVE_CONNECTED_TELEGRAM, RegistrationWork.wait_for_connect),
    InnohassleUserFilter(),
)
async def command_start_handler(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await state.set_state(RegistrationWork.printer_is_not_set)
    printers = await api_client.get_printers_list(message.from_user.id)

    msg = await message.answer(
        f"👋 Hello, {html.bold(html.quote(message.from_user.first_name))}\n"
        f"This is a bot for printing documents with\n{html.bold("Innopolis University printers!")}\n\n"
        "❓ About: /help\n\n"
        f"To proceed, please, {html.bold("choose a printer")}",
        reply_markup=printers_keyboard(printers),
    )

    asyncio.create_task(
        update_printer_statuses(
            message.from_user.id,
            message.chat.id,
            msg.message_id,
            printers,
            state,
            bot,
            checkable_state=RegistrationWork.printer_is_not_set,
        )
    )


@router.callback_query(RegistrationWork.printer_is_not_set, PrinterCallback.filter())
async def registration_work_set_printer(callback: CallbackQuery, callback_data: PrinterCallback, state: FSMContext):
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.delete_reply_markup()
    await state.update_data(printer=callback_data.cups_name)
    await shared_messages.send_something(callback, state)


@router.message(~InnohassleUserFilter())
async def any_not_registered_handler(bot: Bot, event_from_user: types.User, state: FSMContext):
    connect_kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text="Connect",
                    login_url=types.LoginUrl(
                        url="https://innohassle.ru/account/connect-telegram" + f"?bot={(await bot.me()).username}",
                        forward_text="Connect your telegram",
                        bot_username="InNoHassleBot",
                    ),
                )
            ]
        ]
    )
    push_kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=I_HAVE_CONNECTED_TELEGRAM)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    await bot.send_message(
        event_from_user.id,
        "To continue, you need to connect your Telegram account to the InNoHassle account.",
        reply_markup=connect_kb,
    )
    # wait for the user to connect the account
    await asyncio.sleep(3)
    await bot.send_message(
        event_from_user.id,
        "If you have already connected your account, just press the button.",
        reply_markup=push_kb,
    )
