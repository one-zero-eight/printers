import httpx

from src.api.logging_ import logger
from src.config import settings
from src.config_schema import Scanner
from src.modules.scanning.entity_models import ScanningOptions

SCAN_OPTIONS_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<scan:ScanSettings xmlns:pwg="http://www.pwg.org/schemas/2010/12/sm"
                   xmlns:scan="http://schemas.hp.com/imaging/escl/2011/05/03">
    <pwg:Version>2.63</pwg:Version>
    <pwg:ScanRegions>
        <pwg:ScanRegion>
            <pwg:Height>4205</pwg:Height>
            <pwg:Width>2551</pwg:Width>
            <pwg:XOffset>0</pwg:XOffset>
            <pwg:YOffset>0</pwg:YOffset>
        </pwg:ScanRegion>
    </pwg:ScanRegions>
    <scan:InputSource>{input_source}</scan:InputSource>
    <scan:Duplex>{sides}</scan:Duplex>
    <scan:AdfOption>Duplex</scan:AdfOption>
    <scan:EdgeAutoDetection>true</scan:EdgeAutoDetection>
    <scan:ColorMode>RGB24</scan:ColorMode>
    <scan:XResolution>{quality}</scan:XResolution>
    <scan:YResolution>{quality}</scan:YResolution>
    <pwg:DocumentFormat>application/pdf</pwg:DocumentFormat>
</scan:ScanSettings>
"""


class ScanningRepository:
    def get_scanner(self, scanner_name: str) -> Scanner | None:
        for elem in settings.api.scanners_list:
            if elem.name == scanner_name:
                return elem
        return None

    async def get_scanner_capabilities(self, scanner: Scanner):
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(f"{scanner.escl}/ScannerCapabilities")
            response.raise_for_status()
            return response.text  # XML document

    async def get_scanner_status(self, scanner: Scanner):
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(f"{scanner.escl}/ScannerStatus")
            response.raise_for_status()
            return response.text

    async def scan_one_page(self, scanner: Scanner, options: ScanningOptions) -> bytes | None:
        """Scan using eSCL and return document as PDF bytes"""
        try:
            job_id = await self.start_scan_one(scanner, options)
            logger.info(f"Scanner {scanner.name} scanning: {job_id}")
            if not job_id:
                return None
            document = await self._fetch_scanned_document(scanner, job_id)
            await self._delete_printer_scan_job(scanner, job_id)
        except httpx.HTTPError as e:
            logger.info(f"Scanner {scanner.name} error: {e}")
            raise

        return document

    async def start_scan_one(self, scanner: Scanner, options: ScanningOptions) -> str | None:
        """Start scan and return document url which should be checked for file existence"""
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.post(
                url=f"{scanner.escl}/ScanJobs",
                headers={"Content-Type": "application/xml"},
                content=SCAN_OPTIONS_TEMPLATE.format(
                    sides=options.sides, quality=options.quality, input_source=options.input_source
                ),
            )
            if response.status_code == 503:
                logger.info(f"Scanner {scanner.name} status code 503 (scanner is busy)")
                return None
            response.raise_for_status()

            document_url = response.headers.get("Location")
            if not document_url:
                logger.warning(f"Scanner {scanner.name} returned None document url")
                return None

            job_id = document_url.rsplit("/ScanJobs/", 1)[-1]
            return job_id

    async def fetch_scan_one(self, scanner: Scanner, job_id: str) -> bytes | None:
        document = await self._fetch_scanned_document(scanner, job_id)
        await self._delete_printer_scan_job(scanner, job_id)
        return document

    async def _fetch_scanned_document(self, scanner: Scanner, job_id: str) -> bytes:
        async with httpx.AsyncClient(verify=False, timeout=httpx.Timeout(None)) as client:
            logger.info(f"Scanner {scanner.name} fetching document {job_id}")
            response = await client.get(f"{scanner.escl}/ScanJobs/{job_id}/NextDocument")
            response.raise_for_status()
            return response.content  # PDF bytes

    async def _delete_printer_scan_job(self, scanner: Scanner, job_id: str) -> None:
        """Delete the scan job from the printer, so nobody can download the file"""
        async with httpx.AsyncClient(verify=False) as client:
            logger.info(f"Scanner {scanner.name} deleting document {job_id}")
            response = await client.delete(f"{scanner.escl}/ScanJobs/{job_id}")
            response.raise_for_status()


scanning_repository = ScanningRepository()
