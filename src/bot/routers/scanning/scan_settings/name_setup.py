from aiogram import Bot, F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaDocument, Message

from src.bot.api import api_client
from src.bot.routers.printing.printing_tools import discard_job_settings_message
from src.bot.routers.scanning.scanning_states import ScanWork
from src.bot.routers.scanning.scanning_tools import ScanningPausedCallback, format_scanning_paused_message

router = Router(name="scan_name_setup")


async def start_scan_name_setup(callback_or_message: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.set_state(ScanWork.setup_name)

    data = await state.get_data()
    current_scan_name = data.get("scan_name") or "scan.pdf"
    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    msg = await message.answer(
        f"✏️ Send the new name for your scanned document.\n\n"
        f"Current filename: {html.bold(html.quote(current_scan_name))}"
    )
    await state.update_data(job_settings_message_id=msg.message_id)


@router.callback_query(ScanWork.setup_name, ScanningPausedCallback.filter(F.menu == "rename"))
@router.callback_query(ScanWork.pause_menu, ScanningPausedCallback.filter(F.menu == "rename"))
async def scan_options_name(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await start_scan_name_setup(callback, state, bot)


@router.message(ScanWork.setup_name, F.text)
async def apply_settings_name(message: Message, state: FSMContext, bot: Bot):
    await message.delete()

    new_scan_name = message.text.strip()
    if not new_scan_name.lower().endswith(".pdf"):
        new_scan_name = f"{new_scan_name}.pdf"

    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    data = await state.get_data()
    current_scan_name = data.get("scan_name") or "scan.pdf"
    if any(char in new_scan_name for char in invalid_chars):
        assert "job_settings_message_id" in data
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data["job_settings_message_id"],
            text=f"✏️ The name provided contains invalid characters: {html.bold(html.quote(', '.join(invalid_chars)))}\n\n"
            f"Send the new name for your scanned document, current filename: {html.bold(html.quote(current_scan_name))}",
        )
        return

    await discard_job_settings_message(data, message, state, bot)
    await state.update_data(scan_name=new_scan_name)
    assert "confirmation_message_id" in data
    assert "scan_server_name" in data

    file = await api_client.get_scanned_file(message.chat.id, data["scan_server_name"])
    input_file = BufferedInputFile(file, filename=new_scan_name)
    scanner = await api_client.get_scanner(message.chat.id, data.get("scanner"))
    text, markup = format_scanning_paused_message(data, scanner)

    await state.set_state(ScanWork.pause_menu)
    await bot.edit_message_media(
        media=InputMediaDocument(media=input_file, caption=text),
        chat_id=message.chat.id,
        message_id=data["confirmation_message_id"],
        reply_markup=markup,
    )
