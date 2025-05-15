__all__ = ["printing_repository"]

import re

import bs4
import cups
import httpx

from src.config import settings
from src.config_schema import Printer
from src.logging_ import logger
from src.modules.printing.entity_models import JobAttributes, PrinterStatus, PrintingOptions


# noinspection PyMethodMayBeStatic
class PrintingRepository:
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

    def get_printer(self, name: str) -> Printer | None:
        for elem in settings.api.printers_list:
            if elem.name == name:
                return elem
        return None

    def get_printer_status(self, printer: Printer) -> PrinterStatus:
        attributes = self.server.getPrinterAttributes(printer.cups_name, requested_attributes=["marker-levels"])
        logger.info(attributes)

        marker_levels = attributes.get("marker-levels")
        toner_percentage = None
        total_papers = None

        if marker_levels:
            toner_percentage = marker_levels[0]

        try:
            response = httpx.get(f"http://{printer.ip}")
            if response.status_code == httpx.codes.OK:
                html = response.text
                soup = bs4.BeautifulSoup(html, "html.parser")
                # <br>
                # <font color="blue">printer-input-tray:</font> <i>octetString with an unspecified format:</i> <font color="red">type=other;mediafeed=116929;mediaxfeed=82677;mediafeed=116929;mediaxfeed=82677;maxcapacity=-2;level=-2;status=19;name=Auto;</font>
                # <font color="blue">:</font> <i>octetString with an unspecified format:</i> <font color="red">type=sheetFeedAutoNonRemovableTray;mediafeed=116929;mediaxfeed=82677;maxcapacity=100;level=0;status=19;name=MP Tray;</font>
                # <font color="blue">:</font> <i>octetString with an unspecified format:</i> <font color="red">type=sheetFeedAutoNonRemovableTray;mediafeed=116929;mediaxfeed=82677;maxcapacity=500;level=150;status=19;name=Cassette 1;</font>
                # <br>

                # Find "printer-input-tray"
                printer_input_tray = soup.find_next("font", string="printer-input-tray:")
                if printer_input_tray:
                    # find previous <br>
                    previous_br = printer_input_tray.find_previous("br")
                    # find next <br>
                    next_br = printer_input_tray.find_next("br")

                    # get all <font> between previous_br and next_br
                    font_elements = []
                    for element in previous_br.find_all_next():
                        if element == next_br:
                            break
                        if element.name == "font":
                            font_elements.append(element)
                    # get "level=X" from all <font>
                    levels = []
                    regex_pattern = r"level=(\d+)"
                    for font in font_elements:
                        match = re.search(regex_pattern, font.text)
                        if match:
                            levels.append(int(match.group(1)))
                    levels = [lvl for lvl in levels if lvl >= 0]
                    total_papers = sum(levels)
            else:
                logger.warning(f"Printer {printer.name} response: {response.text}")
        except Exception as e:
            logger.warning(e)

        return PrinterStatus(
            printer=printer,
            toner_percentage=toner_percentage,
            total_papers=total_papers,
        )

    def print_file(self, printer: Printer, file_name: str, title: str, options: PrintingOptions) -> int:
        options_dict = options.model_dump(by_alias=True, exclude_none=True)
        return self.server.printFile(printer.cups_name, file_name, title, options=options_dict)

    def get_job_status(self, job_id: int) -> JobAttributes:
        attributes = self.server.getJobAttributes(
            job_id, requested_attributes=["job-state-reasons", "job-printer-state-reasons"]
        )
        return JobAttributes.model_validate(attributes)

    def cancel_job(self, job_id: int):
        self.server.cancelJob(job_id, True)


printing_repository: PrintingRepository = PrintingRepository(
    settings.api.cups_server,
    settings.api.cups_port,
    settings.api.cups_user,
    settings.api.cups_password,
)
