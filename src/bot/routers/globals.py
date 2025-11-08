from aiogram import Bot, F, Router, html
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.interrupts import gracefully_interrupt_state
from src.bot.routers.unauthenticated import I_HAVE_CONNECTED_TELEGRAM
from src.bot.shared_messages import go_to_default_state, send_help

router = Router(name="globals")


@router.message(or_f(Command("start"), F.text == I_HAVE_CONNECTED_TELEGRAM))
async def command_start_handler(message: Message, state: FSMContext, bot: Bot):
    await gracefully_interrupt_state(message, state, bot)
    await state.clear()
    await state.set_state(default_state)

    await message.answer(
        f"👋 Hello, {html.bold(html.quote(message.from_user.first_name))}\nWelcome and enjoy our service!",
        reply_markup=ReplyKeyboardRemove(),
    )
    await send_help(message)
    await go_to_default_state(message, state)


@router.message(Command("help"))
async def command_help_handler(message: Message, state: FSMContext):
    await send_help(message)

    if await state.get_state() == default_state:
        await go_to_default_state(message, state)
