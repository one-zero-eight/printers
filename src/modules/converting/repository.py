__all__ = ["Converting"]

import unoserver.client


class Converting:
    def __init__(self, server="0.0.0.0", port=2003):
        self.client = unoserver.client.UnoClient(server, port)

    def any2pdf(self, inpath: str, outpath: str):
        self.client.convert(inpath=inpath, outpath=outpath)


converting_repository: Converting = Converting()
