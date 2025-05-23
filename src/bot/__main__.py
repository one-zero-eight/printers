import asyncio

import motor.motor_asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.types import ErrorEvent
from aiogram.utils.markdown import hblockquote

import src.bot.logging_  # noqa: F401
from src.bot.dispatcher import CustomDispatcher
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
from src.config import settings


async def main() -> None:
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(settings.bot.database_uri.get_secret_value())
    storage = MongoStorage(
        client=mongo_client,
        db_name=settings.bot.database_db_name,
        collection_name=settings.bot.database_collection_name,
    )
    dispatcher = CustomDispatcher(storage=storage)
    bot = Bot(token=settings.bot.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
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
            await message.answer(
                f"Unknown error ⚠️\n{hblockquote(event.exception)}\nTry /start", disable_web_page_preview=True
            )
        except TelegramBadRequest:
            await message.answer("Unknown error ⚠️\nTry /start", disable_web_page_preview=True)
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
