__all__ = ["Converting", "converting_repository"]

import unoserver.client

from src.config import settings


class Converting:
    def __init__(self, server: str, port: int):
        self.client = unoserver.client.UnoClient(server, str(port), host_location="remote")

    def any2pdf(self, inpath: str, outpath: str):
        self.client.convert(inpath=inpath, outpath=outpath)


converting_repository: Converting = Converting(settings.api.unoserver_server, settings.api.unoserver_port)
