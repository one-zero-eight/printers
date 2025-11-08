import asyncio

import motor.motor_asyncio
from aiogram import Bot, html
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.types import ErrorEvent

import src.bot.logging_  # noqa: F401
from src.bot.dispatcher import CustomDispatcher
from src.bot.logging_ import logger
from src.bot.middlewares import ChatActionMiddleware, LogAllEventsMiddleware
from src.bot.routers.globals import router as globals_router
from src.bot.routers.print_settings.copies_setup import router as print_copies_setup_router
from src.bot.routers.print_settings.layout_setup import router as print_layout_setup_router
from src.bot.routers.print_settings.pages_setup import router as print_pages_setup_router
from src.bot.routers.print_settings.printer_setup import router as print_printer_setup_router
from src.bot.routers.print_settings.sides_setup import router as print_sides_setup_router
from src.bot.routers.printing.printing import router as printing_router
from src.bot.routers.scanning.scan_settings.mode_setup import router as scan_mode_setup_router
from src.bot.routers.scanning.scan_settings.quality_setup import router as scan_quality_setup_router
from src.bot.routers.scanning.scan_settings.scanner_setup import router as scan_scanner_setup_router
from src.bot.routers.scanning.scan_settings.sides_setup import router as scan_sides_setup_router
from src.bot.routers.scanning.scanning import router as scanning_router
from src.bot.routers.unauthenticated import router as unauthenticated_router
from src.bot.shared_messages import usual_error_answer
from src.config import settings


async def main() -> None:
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.bot.database_uri.get_secret_value())
    storage = MongoStorage(
        client=mongo_client,
        db_name=settings.bot.database_db_name,
        collection_name=settings.bot.database_collection_name,
    )
    dispatcher = CustomDispatcher(storage=storage)
    if settings.bot.proxy_url:
        logger.info("Using proxy")
        session = AiohttpSession(proxy=settings.bot.proxy_url.get_secret_value())
    else:
        session = None
    bot = Bot(
        token=settings.bot.bot_token.get_secret_value(),
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    log_all_events_middleware = LogAllEventsMiddleware()
    dispatcher.message.middleware(log_all_events_middleware)
    dispatcher.callback_query.middleware(log_all_events_middleware)
    chat_action_middleware = ChatActionMiddleware()
    dispatcher.message.middleware(chat_action_middleware)
    dispatcher.callback_query.middleware(chat_action_middleware)

    @dispatcher.error()
    async def unhandled_error(event: ErrorEvent):
        message = event.update.callback_query.message if event.update.callback_query else event.update.message
        try:
            if usual_answer := await usual_error_answer(event):
                await message.reply(usual_answer, disable_web_page_preview=True)
            else:
                await message.reply(
                    "Error 🙁\n\n"
                    + html.bold("Try to send the file or /scan again\n")
                    + "Use /start if the error persists"
                    + (f"\n\n{html.spoiler(f'For developers: {event.exception}')}" if str(event.exception) else "")
                )
        except TelegramBadRequest:
            await message.reply(
                "Unknown error ⚠️\n\n"
                + html.bold("Try to send the file or /scan again\n")
                + "Use /start if the error persists",
                disable_web_page_preview=True,
            )
        raise  # noqa: PLE0704

    for router in (
        unauthenticated_router,
        globals_router,
        printing_router,
        scanning_router,
        print_printer_setup_router,
        print_copies_setup_router,
        print_layout_setup_router,
        print_pages_setup_router,
        print_sides_setup_router,
        scan_scanner_setup_router,
        scan_mode_setup_router,
        scan_quality_setup_router,
        scan_sides_setup_router,
    ):
        dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
