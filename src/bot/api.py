import io

import httpx

from src.config import settings


class InNoHasslePrintAPI:
    api_root_path: str

    def __init__(self, api_url):
        self.api_root_path = api_url

    def _create_client(self, telegram_id) -> httpx.AsyncClient:
        client = httpx.AsyncClient(
            base_url=self.api_root_path,
            headers={"Authorization": f"Bearer {telegram_id}:{settings.bot.bot_token.get_secret_value()}"},
        )
        return client

    async def prepare_document(self, telegram_id, document_name, document: io.BytesIO) -> tuple[bool | None, str]:
        files = {"file": (document_name, document, "application/octet-stream")}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/print/prepare", files=files)
            if response.status_code == 400:
                return None, response.json()["detail"]
            if response.status_code == 200:
                return True, response.json()
            response.raise_for_status()

    async def get_prepared_document(self, telegram_id, document_name) -> bytes:
        params = {"filename": document_name}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/get_file", params=params)
            if response.status_code == 200:
                return response.content
            response.raise_for_status()

    async def get_innohassle_user_id(self, telegram_id: int) -> str | None:
        async with self._create_client(telegram_id) as client:
            response = await client.get("/users/my_id")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return
            response.raise_for_status()


api_client: InNoHasslePrintAPI = InNoHasslePrintAPI(settings.bot.api_url)
