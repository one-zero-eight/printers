import io

import httpx

from src.config import settings
from src.config_schema import Printer
from src.modules.printing.entity_models import JobAttributes, PrintingOptions
from src.modules.printing.routes import PreparePrintingResponse


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

    async def prepare_document(
        self, telegram_id: int, document_name: str, document: io.BytesIO
    ) -> tuple[bool | None, PreparePrintingResponse | str]:
        files = {"file": (document_name, document, "application/octet-stream")}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/print/prepare", files=files, timeout=httpx.Timeout(None))
            if response.status_code == 400:
                return None, response.json()["detail"]
            if response.status_code == 200:
                return True, response.json()
            response.raise_for_status()

    async def begin_job(
        self, telegram_id: int, filename: str, printer_name: str, printing_options: PrintingOptions
    ) -> int:
        params = {"filename": filename, "printer_name": printer_name}
        data = {"printing_options": printing_options.model_dump(by_alias=True)}
        async with self._create_client(telegram_id) as client:
            response = await client.post(
                "/print/print",
                params=params,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=httpx.Timeout(None),
            )
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()

    async def check_job(self, telegram_id: int, job_id: int) -> JobAttributes:
        params = {"job_id": job_id}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/job_status", params=params, timeout=httpx.Timeout(None))
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()

    async def cancel_job(self, telegram_id: int, job_id: int) -> None:
        params = {"job_id": job_id}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/print/cancel", params=params)
            if response.status_code == 200:
                return
            response.raise_for_status()

    async def get_prepared_document(self, telegram_id, document_name) -> bytes:
        params = {"filename": document_name}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/get_file", params=params, timeout=httpx.Timeout(None))
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

    async def get_printers_list(self, telegram_id: int) -> list[Printer]:
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/get_printers")
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()


api_client: InNoHasslePrintAPI = InNoHasslePrintAPI(settings.bot.api_url)
