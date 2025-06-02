from aiogram import html
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message

from src.config import settings

MAX_WIDTH_FILLER = " " * 100 + "&#x200D;"

HELP_HTML_MESSAGE = """
🖨 <b>@InnoPrintBot</b> is a bot for printing & scanning documents with <b>Innopolis University printers</b>.

<b>Printing:</b>
• Send a photo or a document to the bot, or forward a message from another chat.
• It will be converted to PDF for printing.
• Check required papers count, printer status (toner amount and paper count).

<b>Scanning:</b>
• Send /scan command.
• Manual Scan mode — place documents on scanner glass and get PDF of one or more pages.
• Auto Scan mode — use scanner's automatic feeder to scan a bunch of papers (supports both-sides scan).

<b>Available printers & scanners:</b>
• 🖨 <a href='https://innohassle.ru/maps?scene=university-floor-1&area=printer-1f'>Reading hall, 1 floor</a> — general printer & scanner.
• 🖨 <a href='https://innohassle.ru/maps?scene=university-floor-3&area=printer-319'>Room 319</a> — students printer & scanner.

🛡 Your files are processed on the IU servers and deleted right after printing or scanning.

📣 All the paper for printing is provided to students by Student Union — <a href='https://t.me/suiu_news/543'>donate to SU Fund</a> to cover expenses.

<i>Troubles with printers? Report to it@innopolis.ru.
Bot is not working? Contact @ArtemSBulgakov.
Found any errors? Fill in the <a href='https://forms.gle/2vMmu4vSoVShvbMw6'>feedback form</a>.
Want to contribute? Check out the <a href='https://github.com/one-zero-eight/printers'>GitHub repository</a>.
Made by @one_zero_eight 💜</i>
"""


async def send_help(message: Message):
    video_id = settings.bot.help_video_id
    if not video_id:
        await message.answer(HELP_HTML_MESSAGE, disable_web_page_preview=True)
        return

    try:
        await message.answer_video(video_id, caption=HELP_HTML_MESSAGE, disable_web_page_preview=True)
    except TelegramBadRequest:
        await message.answer(HELP_HTML_MESSAGE, disable_web_page_preview=True)


async def go_to_default_state(callback_or_message: CallbackQuery | Message, state: FSMContext):
    await state.set_state(default_state)

    message = callback_or_message.message if isinstance(callback_or_message, CallbackQuery) else callback_or_message
    await message.answer(
        html.bold("🖨 We are ready to print or scan!\n")
        + "Just send something to be printed or send /scan to start scanning"
    )
