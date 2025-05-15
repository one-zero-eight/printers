import asyncio
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
from src.logging_ import logger
from src.modules.converting.repository import converting_repository
from src.modules.printing.entity_models import JobAttributes, PrinterStatus, PrintingOptions
from src.modules.printing.repository import printing_repository
from src.pydantic_base import BaseSchema

router = APIRouter(prefix="/print", tags=["Print"])
tempfiles: dict[tuple[str, str], Any] = {}


class PreparePrintingResponse(BaseSchema):
    filename: str
    pages: int


@router.get("/job_status")
async def job_status(job_id: int, _innohassle_user_id: USER_AUTH) -> JobAttributes:
    """
    Returns the status of a job
    """
    status = printing_repository.get_job_status(job_id)
    logger.info(f"Job {job_id} status: {status}")
    return status


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


@router.get("/get_printers_status")
async def get_printers_status(_innohassle_user_id: USER_AUTH) -> list[PrinterStatus]:
    result: list[PrinterStatus] = await asyncio.gather(
        *(printing_repository.get_printer_status(printer) for printer in settings.api.printers_list)
    )

    for status in result:
        logger.info(f"Status {status}")
    return result


@router.post("/prepare", responses={400: {"description": "Unsupported format"}})
async def prepare_printing(file: UploadFile, innohassle_user_id: USER_AUTH) -> PreparePrintingResponse:
    """
    Convert a file to pdf and return the path to the converted file
    """

    if not file.size:
        raise HTTPException(400, "Empty file")
    if not file.filename:
        raise HTTPException(400, "No filename")
    ext = file.filename[file.filename.rfind(".") :]
    if ext == ".pdf":
        f = tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf")
        f.write(await file.read())
        tempfiles[(innohassle_user_id, f.name)] = f
        return PreparePrintingResponse(filename=f.name, pages=len(PyPDF2.PdfReader(f).pages))
    elif ext in [".doc", ".docx", ".png", ".txt", ".jpg", ".md", ".bmp", ".xlsx", ".xls", ".odt", ".ods"]:
        with (
            tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=ext) as in_f,
            tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f,
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
        logger.info(f"Job {job_id} has started")
        os.unlink(filename)
        del tempfiles[(innohassle_user_id, filename)]
        return job_id
    else:
        raise HTTPException(404, "No such file")


@router.post("/cancel", responses={404: {"description": "No such file"}, 400: {"description": "No such printer"}})
async def cancel_printing(job_id: int, _innohassle_user_id: USER_AUTH) -> None:
    logger.info(f"Job {job_id} cancelled")
    printing_repository.cancel_job(job_id)


@router.post("/cancel_preparation", responses={404: {"description": "No such file"}})
async def cancel_preparation(filename: str, innohassle_user_id: USER_AUTH) -> None:
    if (innohassle_user_id, filename) in tempfiles:
        os.unlink(filename)
        del tempfiles[(innohassle_user_id, filename)]
    else:
        raise HTTPException(404, "No such file")
