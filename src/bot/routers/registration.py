import asyncio

from aiogram import Bot, Router, html, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.api import api_client
from src.bot.entry_filters import InnohassleUserFilter
from src.bot.routers.print import PrintWork

router = Router(name="registration")


class RegistrationWork(StatesGroup):
    printer_is_not_set = State()


@router.message(Command("start"), InnohassleUserFilter())
async def command_start_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegistrationWork.printer_is_not_set)
    keyboard = InlineKeyboardBuilder()
    for printer in await api_client.get_printers_list(message.from_user.id):
        keyboard.add(InlineKeyboardButton(text=printer["name"], callback_data=printer["name"]))
    await message.answer(
        f"👋 Hello, {html.bold(message.from_user.first_name)}\n"
        f"This is a bot for printing documents with {html.bold("Innopolis University printers!")}\n\n"
        "❓ About: /help\n\n"
        f"To proceed, please, {html.bold("choose a printer")}",
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(RegistrationWork.printer_is_not_set)
async def registration_work_set_printer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(printer=callback.data)
    await state.set_state(PrintWork.request_file)
    await callback.message.answer(
        html.bold("🖨 We are ready to print!\n") + f"Just send something to be printed\n\n"
        f"Current printer is {html.bold((await state.get_data())["printer"])}"
    )


@router.message(Command("start"), ~InnohassleUserFilter())
async def command_start_not_registered_handler(
    message: Message, bot: Bot, event_from_user: types.User, state: FSMContext
):
    await state.set_state(RegistrationWork.waiting_for_registration)
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
        keyboard=[
            [
                types.KeyboardButton(
                    text="I have connected telegram to InNoHassle account.",
                )
            ]
        ],
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
