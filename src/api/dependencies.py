__all__ = ["USER_AUTH", "get_current_user_auth"]

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.api.exceptions import IncorrectCredentialsException
from src.modules.tokens.repository import TokenRepository

bearer_scheme = HTTPBearer(
    scheme_name="Bearer",
    description="Token from [InNoHassle Accounts](https://api.innohassle.ru/accounts/v0/tokens/generate-my-token)",
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
    try:  # Authorization: Bearer <JWT token>
        token_data = await TokenRepository.verify_user_token(token, IncorrectCredentialsException())
    except IncorrectCredentialsException:  # Authorization: Bearer <user_telegram_id:BOT_TOKEN>
        token_data = await TokenRepository.verify_bot_token(token, IncorrectCredentialsException())
    return token_data


USER_AUTH = Annotated[str, Depends(get_current_user_auth)]
