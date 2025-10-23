from typing import Any

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
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


class CallbackFromConfirmationMessageFilter(Filter):
    async def __call__(self, callback: CallbackQuery, state: FSMContext) -> bool:
        return callback.message.message_id == (await state.get_data()).get("confirmation_message_id", None)
