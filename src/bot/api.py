import io

import httpx
from pydantic import TypeAdapter

from src.config import settings
from src.config_schema import Printer, Scanner
from src.modules.printing.entity_models import JobAttributes, PreparePrintingResponse, PrinterStatus, PrintingOptions
from src.modules.scanning.entity_models import ScannerStatus, ScanningOptions, ScanningResult


class InNoHasslePrintAPI:
    api_root_path: str

    def __init__(self, api_url):
        self.api_root_path = api_url

    def _create_client(self, telegram_id, timeout: float | None = 10) -> httpx.AsyncClient:
        client = httpx.AsyncClient(
            base_url=self.api_root_path,
            headers={"Authorization": f"Bearer {telegram_id}:{settings.bot.bot_token.get_secret_value()}"},
            timeout=httpx.Timeout(timeout),
        )
        return client

    async def prepare_document(
        self, telegram_id: int, document_name: str, document: io.BytesIO
    ) -> PreparePrintingResponse:
        files = {"file": (document_name, document, "application/octet-stream")}
        async with self._create_client(telegram_id, 60 * 5) as client:
            response = await client.post("/print/prepare", files=files)
            response.raise_for_status()
            return PreparePrintingResponse.model_validate(response.json())

    async def begin_job(
        self, telegram_id: int, filename: str, printer_cups_name: str, printing_options: PrintingOptions
    ) -> int:
        params = {"filename": filename, "printer_cups_name": printer_cups_name}
        data = {"printing_options": printing_options.model_dump(by_alias=True)}
        async with self._create_client(telegram_id) as client:
            response = await client.post(
                "/print/print", params=params, json=data, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    async def check_job(self, telegram_id: int, job_id: int) -> JobAttributes:
        params = {"job_id": job_id}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/print/job_status", params=params)
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
        async with self._create_client(telegram_id, 60 * 5) as client:
            response = await client.get("/print/get_file", params=params)
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
        if printer_cups_name is None:
            return None
        printers = await self.get_printers_list(telegram_id)
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

    async def get_scanners_list(self, telegram_id: int) -> list[Scanner]:
        async with self._create_client(telegram_id) as client:
            response = await client.get("/scan/get_scanners")
            response.raise_for_status()
            adapter = TypeAdapter(list[Scanner])
            return adapter.validate_python(response.json())

    async def get_scanner(self, telegram_id: int, scanner_name: str | None = None) -> Scanner | None:
        if scanner_name is None:
            return None
        scanners = await self.get_scanners_list(telegram_id)
        for scanner in scanners:
            if scanner.name == scanner_name:
                return scanner
        return None

    async def get_scanner_status(self, telegram_id: int, scanner_name: str | None = None) -> ScannerStatus | None:
        if scanner_name is None:
            return None
        async with self._create_client(telegram_id) as client:
            response = await client.get("/scan/debug/get_scanner_status", params={"scanner_name": scanner_name})
            response.raise_for_status()
            return ScannerStatus.model_validate(response.json())

    async def start_manual_scan(self, telegram_id: int, scanner: Scanner, scanning_options: ScanningOptions) -> str:
        params = {"scanner_name": scanner.name}
        data = {"scanning_options": scanning_options.model_dump(by_alias=True)}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/scan/manual/start_scan", params=params, json=data)
            response.raise_for_status()
            return response.json()

    async def cancel_manual_scan(self, telegram_id: int, scanner: Scanner, job_id: str) -> None:
        params = {"scanner_name": scanner.name, "job_id": job_id}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/scan/manual/cancel_scan", params=params)
            response.raise_for_status()

    async def wait_and_merge_manual_scan(
        self, telegram_id: int, scanner: Scanner, job_id: str, prev_filename: str | None
    ) -> ScanningResult | None:
        params = {"scanner_name": scanner.name, "job_id": job_id}
        if prev_filename:
            params["prev_filename"] = prev_filename
        async with self._create_client(telegram_id, 60 * 5) as client:
            response = await client.post("/scan/manual/wait_and_merge", params=params)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return ScanningResult.model_validate(response.json())

    async def remove_last_page_manual_scan(self, telegram_id: int, filename: str) -> ScanningResult:
        params = {"filename": filename}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/scan/manual/remove_last_page", params=params)
            response.raise_for_status()
            return ScanningResult.model_validate(response.json())

    async def get_scanned_file(self, telegram_id: int, filename: str) -> bytes:
        params = {"filename": filename}
        async with self._create_client(telegram_id) as client:
            response = await client.get("/scan/get_file", params=params)
            response.raise_for_status()
            return response.content

    async def delete_scanned_file(self, telegram_id: int, filename: str) -> None:
        params = {"filename": filename}
        async with self._create_client(telegram_id) as client:
            response = await client.post("/scan/manual/delete_file", params=params)
            response.raise_for_status()


api_client: InNoHasslePrintAPI = InNoHasslePrintAPI(settings.bot.api_url)
