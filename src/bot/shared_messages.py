from aiogram import html
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.bot.api import api_client
from src.bot.routers.printing.printing_states import PrintWork
from src.modules.printing.entity_models import JobAttributes, JobStateEnum


async def send_something(callback: CallbackQuery, state: FSMContext, job_attributes: JobAttributes | None = None):
    await state.set_state(PrintWork.request_file)
    note = None
    if job_attributes:  # Previous job was printed
        if job_attributes.job_state == JobStateEnum.canceled:
            note = "❌ Job was canceled"
        elif job_attributes.job_state == JobStateEnum.aborted:
            note = "❌ Job was aborted"
        elif job_attributes.job_state == JobStateEnum.completed:
            note = "✅ Job was completed"
    text = ""
    if note:
        text = f"{note}\n\n"
    text += html.bold("🖨 We are ready to print!\n") + "Just send something to be printed"

    printer_cups_name = (await state.get_data())["printer"]
    printer = await api_client.get_printer(callback.from_user.id, printer_cups_name)
    if printer is not None:
        text += f"\n\nCurrent printer is {html.bold(html.quote(printer.display_name))}"

    await callback.message.answer(text)
