__all__ = ["TokenRepository"]

import time

from authlib.jose import JoseError, JWTClaims, jwt

from src.config import settings
from src.modules.innohassle_accounts import innohassle_accounts


class TokenRepository:
    @classmethod
    def decode_token(cls, token: str) -> JWTClaims:
        now = time.time()
        pub_key = innohassle_accounts.get_public_key()
        payload = jwt.decode(token, pub_key)
        payload.validate_exp(now, leeway=0)
        payload.validate_iat(now, leeway=0)
        return payload

    @classmethod
    async def verify_user_token(cls, token: str, credentials_exception) -> str:
        try:
            payload = cls.decode_token(token)
            innohassle_id: str = payload.get("uid")
            if innohassle_id is None:
                raise credentials_exception
            return innohassle_id
        except JoseError:
            raise credentials_exception

    @classmethod
    async def verify_bot_token(cls, token: str, credentials_exception) -> str:
        if token.endswith(settings.bot.bot_token.get_secret_value()):
            telegram_id = token[: -len(settings.bot.bot_token.get_secret_value())]
            if telegram_id:
                telegram_id = int(telegram_id.strip(":"))
                innohassle_user = await innohassle_accounts.get_user_by_telegram_id(telegram_id)
                if innohassle_user:
                    return innohassle_user.id
        raise credentials_exception
