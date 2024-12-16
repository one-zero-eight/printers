__all__ = ["Converting"]

import os

import unoserver.client


class Converting:
    def __init__(self, server="0.0.0.0", port=2003):
        self.client = unoserver.client.UnoClient(server, port)

    def conversion_is_allowed(self, filename: str):
        return filename[filename.rfind(".") + 1 :] in [
            "doc",
            "docx",
            "png",
            "txt",
            "jpg",
            "md",
            "bmp",
            "xlsx",
            "xls",
            "odt",
            "ods",
        ]

    def any2pdf(self, filename: str):
        if not self.conversion_is_allowed(filename):
            print("The file cannot be converted.")
            return
        filepath = (here := os.path.dirname(__file__))[: here.index("src")] + f"files_to_be_printed/{filename}"
        self.client.convert(inpath=filepath, outpath=f"{filepath[:filepath.rfind('.')]}.pdf")


converting_repository: Converting = Converting()
