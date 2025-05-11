import os
import pathlib
import tempfile
from typing import Any

import PyPDF2
from fastapi import APIRouter, Body, UploadFile
from fastapi.exceptions import HTTPException
from starlette.responses import FileResponse

from src.api.dependencies import USER_AUTH
from src.config import settings
from src.config_schema import Printer
from src.modules.converting.repository import converting_repository
from src.modules.printing.entity_models import JobAttributes, PrintingOptions
from src.modules.printing.repository import printing_repository
from src.pydantic_base import BaseSchema

router = APIRouter(prefix="/print", tags=["Print"])
tempfiles: dict[tuple[str, str], Any] = {}
dir_for_temp = os.getcwd() + "/tmp"


class PreparePrintingResponse(BaseSchema):
    filename: str
    pages: int


@router.get("/job_status")
async def job_status(job_id: int, _innohassle_user_id: USER_AUTH) -> JobAttributes:
    """
    Returns the status of a job
    """

    return printing_repository.get_job_status(job_id)


@router.get("/get_file", responses={404: {"description": "No such file"}})
def get_file(filename: str, innohassle_user_id: USER_AUTH) -> FileResponse:
    if (innohassle_user_id, filename) in tempfiles:
        short_name = pathlib.Path(filename).name
        return FileResponse(filename, headers={"Content-Disposition": f"attachment; filename={short_name}"})
    else:
        raise HTTPException(404, "No such file")


@router.get("/get_printers")
def get_printers(_innohassle_user_id: USER_AUTH) -> list[Printer]:
    return settings.api.printers_list


@router.post("/prepare", responses={400: {"description": "Unsupported format"}})
async def prepare_printing(file: UploadFile, innohassle_user_id: USER_AUTH) -> PreparePrintingResponse:
    """
    Convert a file to pdf and return the path to the converted file
    """

    if not file.size:
        raise HTTPException(400, "Empty file")
    ext = file.filename[file.filename.rfind(".") :]
    if ext == ".pdf":
        f = tempfile.NamedTemporaryFile(dir=dir_for_temp, suffix=".pdf")
        f.write(await file.read())
        tempfiles[(innohassle_user_id, f.name)] = f
        return PreparePrintingResponse(filename=f.name, pages=len(PyPDF2.PdfReader(f).pages))
    elif ext in [".doc", ".docx", ".png", ".txt", ".jpg", ".md", ".bmp", ".xlsx", ".xls", ".odt", ".ods"]:
        with (
            tempfile.NamedTemporaryFile(dir=dir_for_temp, suffix=ext) as in_f,
            tempfile.NamedTemporaryFile(dir=dir_for_temp, suffix=".pdf", delete=False) as out_f,
        ):
            in_f.write(await file.read())
            in_f.flush()
            converting_repository.any2pdf(in_f.name, out_f.name)
            in_f.close()
            tempfiles[(innohassle_user_id, out_f.name)] = out_f
            return PreparePrintingResponse(filename=out_f.name, pages=len(PyPDF2.PdfReader(out_f).pages))
    else:
        raise HTTPException(400, f"no support of the {ext} format")


@router.post("/print", responses={404: {"description": "No such file"}, 400: {"description": "No such printer"}})
async def actual_print(
    filename: str,
    printer_name: str,
    innohassle_user_id: USER_AUTH,
    printing_options: PrintingOptions = Body(PrintingOptions(), embed=True),
) -> int:
    """
    Returns job identifier
    """

    if (innohassle_user_id, filename) in tempfiles:
        printer = printing_repository.get_printer(printer_name)
        if not printer:
            raise HTTPException(400, "No such printer")
        job_id = printing_repository.print_file(printer, filename, "job", printing_options)
        os.unlink(filename)
        del tempfiles[(innohassle_user_id, filename)]
        return job_id
    else:
        raise HTTPException(404, "No such file")


@router.post("/cancel", responses={404: {"description": "No such file"}, 400: {"description": "No such printer"}})
async def cancel_printing(job_id: int, _innohassle_user_id: USER_AUTH):
    printing_repository.cancel_job(job_id)
