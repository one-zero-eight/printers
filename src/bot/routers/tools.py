import asyncio

from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, Message

from src.bot.logging_ import logger

expiration_tasks = set()
message_expiration_time = 5 * 60 * 60


def button_text_align_left(string):
    return string + " " * (100 - len(string)) + "."


async def ensure_same_structural_message(structural_message: Message, fsm_message_id: str, state: FSMContext):
    if (await state.get_data()).get(fsm_message_id) != structural_message.message_id:
        if fsm_message_id == "confirmation_message_id":
            logger.warning("The confirmation message was changed")
            await mark_as_expired(structural_message, True)
            await cancel_expiring(structural_message)
        raise TelegramBadRequest(None, "")


async def make_expiring(message: Message):
    task = asyncio.create_task(mark_as_expired(message), name=str(message.message_id))
    expiration_tasks.add(task)
    task.add_done_callback(lambda elem: expiration_tasks.remove(elem))


async def cancel_expiring(message: Message):
    for elem in expiration_tasks:
        if elem.get_name() == str(message.message_id):
            elem.cancel()
            return


async def mark_as_expired(message: Message, immediately: bool = False):
    await asyncio.sleep(0 if immediately else message_expiration_time)
    await edit_message_text_anyway(
        message=message, text=f"{message.caption or message.text}\n{html.italic('This job has expired 🕒')}"
    )


async def edit_message_text_anyway(message: Message, text: str, reply_markup: InlineKeyboardMarkup | None = None):
    try:
        await message.edit_caption(caption=text, reply_markup=reply_markup)
    except TelegramBadRequest:
        try:
            await message.edit_text(text=text, reply_markup=reply_markup)
        except TelegramBadRequest:
            pass
