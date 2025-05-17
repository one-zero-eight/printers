import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import ErrorEvent
from aiogram.utils.markdown import hblockquote

import src.bot.logging_  # noqa: F401
from src.bot.dispatcher import CustomDispatcher
from src.bot.middlewares import ChatActionMiddleware, LogAllEventsMiddleware
from src.bot.routers.print_settings.copies_setup import router as copies_setup_router
from src.bot.routers.print_settings.layout_setup import router as layout_setup_router
from src.bot.routers.print_settings.pages_setup import router as pages_setup_router
from src.bot.routers.print_settings.printer_choice import router as printer_choice_router
from src.bot.routers.print_settings.sides_setup import router as sides_setup_router
from src.bot.routers.printing.printing import router as printing_router
from src.bot.routers.registration import router as registration_router
from src.config import settings


async def main() -> None:
    dispatcher = CustomDispatcher()
    bot = Bot(token=settings.bot.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    log_all_events_middleware = LogAllEventsMiddleware()
    dispatcher.message.middleware(log_all_events_middleware)
    dispatcher.callback_query.middleware(log_all_events_middleware)
    chat_action_middleware = ChatActionMiddleware()
    dispatcher.message.middleware(chat_action_middleware)
    dispatcher.callback_query.middleware(chat_action_middleware)

    @dispatcher.error()
    async def unhandled_error(event: ErrorEvent):
        update = event.update
        if update.message is not None:
            await update.message.answer(f"Unknown error ⚠️\n{hblockquote(event.exception)}")
        elif update.callback_query is not None:
            await update.callback_query.answer(f"Unknown error ⚠️\n{hblockquote(event.exception)}")
        raise  # noqa: PLE0704

    for router in (
        registration_router,
        printing_router,
        printer_choice_router,
        copies_setup_router,
        layout_setup_router,
        pages_setup_router,
        sides_setup_router,
    ):
        dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
