from aiogram import html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.routers.printing.printing_states import PrintWork


async def send_something(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PrintWork.request_file)
    await callback.message.answer(
        html.bold("🖨 We are ready to print!\n") + f"Just send something to be printed\n\n"
        f"Current printer is {html.bold((await state.get_data())["printer"])}"
    )
