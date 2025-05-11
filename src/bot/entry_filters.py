from typing import Any

from aiogram.filters import Filter
from aiogram.types import (
    TelegramObject,
    User,
)

from src.bot.api import api_client


class InnohassleUserFilter(Filter):
    async def __call__(self, event: TelegramObject, event_from_user: User) -> bool | dict[str, Any]:
        telegram_id = event_from_user.id
        innohassle_user_id = await api_client.get_innohassle_user_id(telegram_id)
        if innohassle_user_id is None:
            return False
        return {"innohassle_user_id": innohassle_user_id}
