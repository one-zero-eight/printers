import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.routers.copies_setup import router as copies_setup_router
from src.bot.routers.layout_setup import router as layout_setup_router
from src.bot.routers.pages_setup import router as pages_setup_router
from src.bot.routers.print import router as print_router
from src.bot.routers.printer_choice import router as printer_choice_router
from src.bot.routers.registration import router as registration_router
from src.bot.routers.sides_setup import router as sides_setup_router
from src.config import settings


async def main() -> None:
    dispatcher = Dispatcher()
    bot = Bot(token=settings.bot.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    for router in (
        registration_router,
        print_router,
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
