import tempfile
from io import BytesIO

import PyPDF2

from src.config import settings


def merge_documents(document: bytes, tempfile_f):
    """
    Merge documents tempfile_f and document to out_f using PyPDF2
    """

    with tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f:
        merger = PyPDF2.PdfMerger()
        merger.append(tempfile_f.name)
        merger.append(BytesIO(document))
        merger.write(out_f.name)
        merger.close()
        return out_f
