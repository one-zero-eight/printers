__all__ = ["USER_AUTH", "get_current_user_auth"]

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.exceptions import IncorrectCredentialsException
from src.config import settings
from src.modules.inh_accounts_sdk import inh_accounts

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Token from [InNoHassle Accounts](https://innohassle.ru/account/token)",
    bearerFormat="JWT",
    auto_error=False,  # We'll handle error manually
)


async def get_current_user_auth(bearer: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    """
    Returns InNoHassle Accounts user id
    """
    token = bearer and bearer.credentials
    if not token:
        raise IncorrectCredentialsException(no_credentials=True)

    # Check bot authorization:
    # Authorization: Bearer <user_telegram_id:BOT_TOKEN>
    bot_auth = await verify_bot_token(token)
    if bot_auth:
        return bot_auth

    # Check user authorization:
    # Authorization: Bearer <JWT token>
    token_data = inh_accounts.decode_token(token)
    if token_data:
        return token_data.innohassle_id

    raise IncorrectCredentialsException(no_credentials=False)


async def verify_bot_token(token: str) -> str | None:
    if token.endswith(settings.bot.bot_token.get_secret_value()):
        telegram_id = token[: -len(settings.bot.bot_token.get_secret_value())]
        if telegram_id:
            telegram_id = int(telegram_id.strip(":"))
            innohassle_user = await inh_accounts.get_user(telegram_id=telegram_id)
            if innohassle_user:
                return innohassle_user.id
    return None


USER_AUTH = Annotated[str, Depends(get_current_user_auth)]
