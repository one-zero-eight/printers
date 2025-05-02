import asyncio
import io

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.api import api_client

TOKEN = "PASTE_YOUR_TOKEN"

dispatcher = Dispatcher()
router = Router()

main_menu_reply_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Print")],
        [KeyboardButton(text="Select printer"), KeyboardButton(text="Printer settings")],
        [KeyboardButton(text="Bot features")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Press an action button!",
)
removed_reply_keyboard = ReplyKeyboardRemove(remove_keyboard=True)


class PrintWork(StatesGroup):
    request_file = State()
    wait_for_acceptance = State()


class SelectPrinter(StatesGroup):
    selection = State()


@router.message(Command("start"))
async def command_start_handler(message: Message):
    await message.answer(
        f"Hello, {html.bold(message.from_user.first_name)}\n\n"
        f"This bot will help you to print with {html.bold("Innopolis public printers!")}\n\n"
        f"Use keyboard buttons to setup a printer, get more information, or start printing!",
        reply_markup=main_menu_reply_keyboard,
    )


@router.message(F.text == "Print")
async def print_work_request_file(message: Message, state: FSMContext):
    await state.set_state(PrintWork.request_file)
    await message.answer("Print work has been started", reply_markup=removed_reply_keyboard)
    await message.answer(
        "Send here something to be printed",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Cancel", callback_data="Cancel")]]
        ),
    )


@router.callback_query(lambda call: call.data == "Cancel" or call.data == "Reject")
async def print_work_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer("Print work have been cancelled", reply_markup=main_menu_reply_keyboard)


@router.callback_query(PrintWork.wait_for_acceptance)
async def print_work_print(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.answer(
        "This function is in development. Let printing is succeed!", reply_markup=main_menu_reply_keyboard
    )


@router.message(PrintWork.request_file)
async def print_work_confirmation(message: Message, state: FSMContext):
    if not any((message.document, message.photo, message.text)):
        await message.answer("Only documents, photos, and text messages are supported to be printed")
        return
    await message.answer("Processing started...")
    file_telegram_identifier = (
        message.document.file_id if message.document else message.photo[-1].file_id if message.photo else None
    )
    file_telegram_name = (
        message.document.file_name if message.document else "Photo.png" if message.photo else "Text.txt"
    )
    file = io.BytesIO()
    if message.document or message.photo:
        await message.bot.download(file=file_telegram_identifier, destination=file)
    else:
        file = io.BytesIO(message.text.encode("utf8"))
    status, detail = await api_client.prepare_document(file_telegram_name, file)
    if status is None:
        await message.answer(
            f"Unfortunately, we cannot print this file yet\n"
            f"because of {html.bold(detail)}\n\n"
            f"Please, send a file of a supported type:\n"
            f"{html.blockquote(".doc\n.docx\n.png\n.txt\n"
                                                ".jpg\n.md\n.bmp\n.xlsx\n.xls\n.odt\n.ods")}"
        )
        return
    document = await api_client.get_prepared_document(detail)
    await message.answer_document(
        (
            document := BufferedInputFile(
                document, filename=file_telegram_name[: file_telegram_name.rfind(".")] + ".pdf"
            )
        ),
        caption="Please, confirm or reject the printing",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Confirm", callback_data="Confirm"),
                    InlineKeyboardButton(text="Reject", callback_data="Reject"),
                ]
            ]
        ),
    )
    await state.set_state(PrintWork.wait_for_acceptance)
    await state.update_data(request_file=document)


@router.message(F.text == "Select printer")
async def command_select_printer(message: Message, state: FSMContext) -> None:
    await state.set_state(SelectPrinter.selection)
    await message.answer("Search for printers...", reply_markup=removed_reply_keyboard)
    keyboard = InlineKeyboardBuilder()
    for printer in ["Printer 1", "Printer 2"]:
        keyboard.add(InlineKeyboardButton(text=printer, callback_data=printer))
    await message.answer("Choose a printer", reply_markup=keyboard.as_markup())


@router.callback_query(SelectPrinter.selection)
async def callback_printer_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.answer(f"You have chosen {callback.data}!", reply_markup=main_menu_reply_keyboard)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
