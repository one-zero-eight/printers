import io

import httpx


class InNoHasslePrintAPI:
    api_root_path: str

    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        self.api_root_path = api_url

    def _create_client(self) -> httpx.AsyncClient:
        client = httpx.AsyncClient(base_url=self.api_root_path)
        return client

    async def prepare_document(self, document_name, document: io.BytesIO) -> tuple[bool | None, str]:
        files = {"file": (document_name, document, "application/octet-stream")}
        async with self._create_client() as client:
            response = await client.post("/print/prepare", files=files)
            if response.status_code == 400:
                return None, response.json()["detail"]
            if response.status_code == 200:
                return True, response.json()
            response.raise_for_status()

    async def get_prepared_document(self, document_name) -> bytes:
        params = {"filename": document_name}
        async with self._create_client() as client:
            response = await client.get("/print/get_file", params=params)
            if response.status_code == 200:
                return response.content
            response.raise_for_status()


api_client: InNoHasslePrintAPI = InNoHasslePrintAPI()
