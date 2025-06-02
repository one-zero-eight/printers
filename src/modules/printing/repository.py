__all__ = ["printing_repository"]

import re
import time

import bs4
import cups
import httpx
from cachetools import TTLCache

from src.api.logging_ import logger
from src.config import settings
from src.config_schema import Printer
from src.modules.printing.entity_models import JobAttributes, PrinterStatus, PrintingOptions


# noinspection PyMethodMayBeStatic
class PrintingRepository:
    server: cups.Connection

    def __init__(self, server: str | None, port: int | None, user: str | None, password: str | None):
        # Settings should be set before calling cups.Connection()
        if server is not None:
            cups.setServer(server)
        if port is not None:
            cups.setPort(port)
        if user is not None:
            cups.setUser(user)
        if password is not None:

            def callback(prompt):
                logger.info(prompt)
                return password

            cups.setPasswordCB(callback)

        self.server = cups.Connection()
        # Cache printer paper status for 5 minutes
        self._printer_paper_status_cache = TTLCache(maxsize=100, ttl=5 * 60)
        # Cache printer toner status for 5 minutes
        self._printer_toner_status_cache = TTLCache(maxsize=100, ttl=5 * 60)

    def get_printer(self, cups_name: str) -> Printer | None:
        for elem in settings.api.printers_list:
            if elem.cups_name == cups_name:
                return elem
        return None

    async def get_printer_status(self, printer: Printer, use_cache: bool = True) -> PrinterStatus:
        toner_percentage = None  # self._fetch_toner_status(printer, use_cache) - shows 0 for our printers
        paper_percentage = None

        async with httpx.AsyncClient() as client:
            offline = await self._is_printer_offline(printer, client)

            if offline:  # only from cache
                paper_percentage = self._printer_paper_status_cache.get(printer.ipp)
            else:  # otherwise fetch from printer, or from cache if ttl is not expired
                try:
                    paper_percentage = await self._fetch_paper_status(printer, client, use_cache)
                except Exception as e:
                    logger.warning(e)

        return PrinterStatus(
            printer=printer,
            offline=offline,
            toner_percentage=toner_percentage,
            paper_percentage=paper_percentage,
        )

    def _fetch_toner_status(self, printer: Printer, use_cache: bool = True) -> int | None:
        # Check cache first
        cached_toner = self._printer_toner_status_cache.get(printer.cups_name)
        if cached_toner is not None and use_cache:
            logger.info(f"Using cached toner percentage for printer {printer.cups_name}")
            return cached_toner

        try:
            t1 = time.perf_counter()
            attributes = self.server.getPrinterAttributes(printer.cups_name, requested_attributes=["marker-levels"])
            t2 = time.perf_counter()
            logger.info(f"Printer {printer.cups_name} get attributes time: {(t2 - t1) * 1000:.0f}ms")

            marker_levels = attributes.get("marker-levels")
            if marker_levels:
                toner_percentage = marker_levels[0]
                # Cache the toner percentage
                self._printer_toner_status_cache[printer.cups_name] = toner_percentage
                return toner_percentage
        except cups.IPPError as e:
            logger.warning(e)
        return None

    async def _is_printer_offline(self, printer: Printer, client: httpx.AsyncClient) -> bool:
        try:
            response = await client.head(f"http://{printer.ipp}")
            logger.info(
                f"Printer {printer.cups_name} (HEAD http://{printer.ipp}) fetch time: {response.elapsed.total_seconds() * 1000:.0f}ms"
            )
            if response.status_code == httpx.codes.METHOD_NOT_ALLOWED:
                return False  # online
            else:
                logger.warning(f"Printer {printer.cups_name} unexpected response: {response}")
                return True
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            logger.warning(f"Printer {printer.cups_name} is offline: {e}")
            return True

    async def _fetch_paper_status(
        self, printer: Printer, client: httpx.AsyncClient, use_cache: bool = True
    ) -> int | None:
        # Check cache first
        cache_key = printer.ipp
        cached = self._printer_paper_status_cache.get(cache_key)
        if cached is not None and use_cache:
            logger.info(f"Using cached paper percentage for printer {printer.cups_name}")
            return cached

        response = await client.get(f"http://{printer.ipp}")
        logger.info(
            f"Printer {printer.cups_name} (GET http://{printer.ipp}) fetch time: {response.elapsed.total_seconds() * 1000:.0f}ms"
        )
        if response.status_code == httpx.codes.OK:
            t1 = time.perf_counter()
            percentage = self._parse_paper_percentage(response.text)
            t2 = time.perf_counter()
            logger.info(f"Printer {printer.cups_name} parse time: {(t2 - t1) * 1000:.0f}ms")
            if percentage is not None:
                # Cache the result
                self._printer_paper_status_cache[cache_key] = percentage
                return percentage
        else:
            logger.warning(f"Printer {printer.cups_name} response: {response}")
        return None

    def _parse_paper_percentage(self, html: str) -> int | None:
        soup = bs4.BeautifulSoup(html, "html.parser")
        # Find "printer-input-tray"
        printer_input_tray = soup.find("font", string="printer-input-tray:")
        if printer_input_tray:
            # find previous <br>
            previous_br = printer_input_tray.find_previous("br")
            if previous_br is None:
                logger.warning("Previous_br is None")
                return None
            # find next <br>
            next_br = printer_input_tray.find_next("br")
            if next_br is None:
                logger.warning("Next_br is None")
                return None

            # get all <font> between previous_br and next_br
            font_elements = []
            for element in previous_br.find_all_next():
                if element == next_br:
                    break
                if isinstance(element, bs4.element.Tag) and element.name == "font":
                    font_elements.append(element)

            # Find Cassette tray and get its level and maxcapacity
            for font in font_elements:
                if "Cassette" in font.text:
                    # Extract level and maxcapacity using regex
                    level_match = re.search(r"level=(\d+)", font.text)
                    maxcapacity_match = re.search(r"maxcapacity=(\d+)", font.text)

                    if level_match and maxcapacity_match:
                        level = int(level_match.group(1))
                        maxcapacity = int(maxcapacity_match.group(1))

                        if maxcapacity > 0:
                            return int((level / maxcapacity) * 100)
        return None

    def print_file(self, printer: Printer, file_name: str, title: str, options: PrintingOptions) -> int:
        options_dict = options.model_dump(by_alias=True, exclude_none=True)
        return self.server.printFile(printer.cups_name, file_name, title, options=options_dict)

    def get_job_status(self, job_id: int) -> JobAttributes:
        attributes = self.server.getJobAttributes(
            job_id,
            requested_attributes=[
                "job-state",
                "job-state-reasons",
                "job-state-message",
                "job-printer-state-reasons",
                "job-printer-state-message",
            ],
        )

        return JobAttributes(
            job_state=attributes["job-state"],
            job_state_reasons=JobAttributes.parse_job_state_reasons(attributes.get("job-state-reasons", "")),
            job_state_message=attributes.get("job-state-message"),
            printer_state_reasons=JobAttributes.parse_printer_state(attributes.get("job-printer-state-reasons", [])),
            printer_state_message=attributes.get("job-printer-state-message"),
        )

    def cancel_job(self, job_id: int):
        self.server.cancelJob(job_id, True)


printing_repository: PrintingRepository = PrintingRepository(
    settings.api.cups_server,
    settings.api.cups_port,
    settings.api.cups_user,
    settings.api.cups_password.get_secret_value() if settings.api.cups_password else None,
)
