from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.routers.printing.printing_states import gracefully_interrupt_printing_state
from src.bot.routers.scanning.scanning_states import gracefully_interrupt_scanning_state

UNINTERRUPTIBLE_STATES = []


async def gracefully_interrupt_state(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await gracefully_interrupt_printing_state(callback_or_message, state, bot)
    await gracefully_interrupt_scanning_state(callback_or_message, state, bot)
