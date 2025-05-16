import io

import httpx
from pydantic import TypeAdapter

from src.config import settings
from src.config_schema import Printer
from src.modules.printing.entity_models import JobAttributes, PrinterStatus, PrintingOptions
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
    ) -> PreparePrintingResponse:
        files = {"file": (document_name, document, "application/octet-stream")}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/print/prepare", files=files, timeout=httpx.Timeout(None))
            response.raise_for_status()
            return PreparePrintingResponse.model_validate(response.json())

    async def begin_job(
        self, telegram_id: int, filename: str, printer_cups_name: str, printing_options: PrintingOptions
    ) -> int:
        params = {"filename": filename, "printer_cups_name": printer_cups_name}
        data = {"printing_options": printing_options.model_dump(by_alias=True)}
        async with self._create_client(telegram_id) as client:
            response = await client.post(
                "/print/print",
                params=params,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=httpx.Timeout(None),
            )
            response.raise_for_status()
            return response.json()

    async def check_job(self, telegram_id: int, job_id: int) -> JobAttributes:
        params = {"job_id": job_id}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/job_status", params=params, timeout=httpx.Timeout(None))
            response.raise_for_status()
            return JobAttributes.model_validate(response.json())

    async def cancel_job(self, telegram_id: int, job_id: int) -> None:
        params = {"job_id": job_id}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/print/cancel", params=params)
            response.raise_for_status()

    async def cancel_not_started_job(self, telegram_id: int, document_name: str) -> None:
        params = {"filename": document_name}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/print/cancel_preparation", params=params)
            response.raise_for_status()

    async def get_prepared_document(self, telegram_id: int, document_name: str) -> bytes:
        params = {"filename": document_name}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/get_file", params=params, timeout=httpx.Timeout(None))
            response.raise_for_status()
            return response.content

    async def get_innohassle_user_id(self, telegram_id: int) -> str | None:
        async with self._create_client(telegram_id) as client:
            response = await client.get("/users/my_id")
            if response.status_code == 401:
                return None
            response.raise_for_status()
            return response.json()

    async def get_printers_list(self, telegram_id: int) -> list[Printer]:
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/get_printers")
            response.raise_for_status()
            adapter = TypeAdapter(list[Printer])
            return adapter.validate_python(response.json())

    async def get_printer(self, telegram_id: int, printer_cups_name: str | None = None) -> Printer | None:
        printers = await self.get_printers_list(telegram_id)
        if printer_cups_name is None:
            return printers[0] if printers else None
        for printer in printers:
            if printer.cups_name == printer_cups_name:
                return printer
        return None

    async def get_printers_status_list(self, telegram_id: int) -> list[PrinterStatus]:
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/get_printers_status")
            response.raise_for_status()
            adapter = TypeAdapter(list[PrinterStatus])
            return adapter.validate_python(response.json())

    async def get_printer_status(self, telegram_id: int, printer_cups_name: str) -> PrinterStatus:
        params = {"printer_cups_name": printer_cups_name}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/get_printer_status", params=params)
            response.raise_for_status()
            return PrinterStatus.model_validate(response.json())


api_client: InNoHasslePrintAPI = InNoHasslePrintAPI(settings.bot.api_url)
