import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any

import PyPDF2
from fastapi import APIRouter, Body, UploadFile
from fastapi.exceptions import HTTPException
from starlette.responses import FileResponse

from src.api.dependencies import USER_AUTH
from src.api.logging_ import logger
from src.config import settings
from src.config_schema import Printer
from src.modules.converting.repository import converting_repository
from src.modules.printing.entity_models import JobAttributes, PreparePrintingResponse, PrinterStatus, PrintingOptions
from src.modules.printing.repository import printing_repository

router = APIRouter(prefix="/print", tags=["Print"])
tempfiles: dict[tuple[str, str], Any] = {}


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
        full_path = tempfiles[(innohassle_user_id, filename)].name
        return FileResponse(full_path, headers={"Content-Disposition": f"attachment; filename={filename}"})
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


@router.get("/get_printer_status")
async def get_printer_status(printer_cups_name: str, _innohassle_user_id: USER_AUTH) -> PrinterStatus:
    printer = printing_repository.get_printer(printer_cups_name)
    if not printer:
        raise HTTPException(400, "No such printer")
    status = await printing_repository.get_printer_status(printer)
    logger.info(f"Printer {printer.cups_name} status: {status}")
    return status


@router.post("/prepare", responses={400: {"description": "Unsupported format"}})
async def prepare_printing(file: UploadFile, innohassle_user_id: USER_AUTH) -> PreparePrintingResponse:
    """
    Convert a file to pdf and return the path to the converted file
    """

    if not file.size:
        raise HTTPException(400, "Empty file")
    if not file.filename:
        raise HTTPException(400, "No filename")
    ext = file.filename[file.filename.rfind(".") :].lower()
    if ext == ".pdf":
        f = tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf")
        f.write(await file.read())
        tempfiles[(innohassle_user_id, Path(f.name).name)] = f
        return PreparePrintingResponse(filename=Path(f.name).name, pages=len(PyPDF2.PdfReader(f).pages))
    elif ext in [".doc", ".docx", ".png", ".txt", ".jpg", ".md", ".bmp", ".xlsx", ".xls", ".odt", ".ods"]:
        with (
            tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=ext) as in_f,
            tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f,
        ):
            in_f.write(await file.read())
            in_f.flush()
            # Run conversion in a background thread
            await asyncio.to_thread(converting_repository.any2pdf, in_f.name, out_f.name)
            in_f.close()
            tempfiles[(innohassle_user_id, Path(out_f.name).name)] = out_f
            return PreparePrintingResponse(filename=Path(out_f.name).name, pages=len(PyPDF2.PdfReader(out_f).pages))
    else:
        raise HTTPException(400, f"no support of the {ext} format")


@router.post("/print", responses={404: {"description": "No such file"}, 400: {"description": "No such printer"}})
async def actual_print(
    filename: str,
    printer_cups_name: str,
    innohassle_user_id: USER_AUTH,
    printing_options: PrintingOptions = Body(PrintingOptions(), embed=True),
) -> int:
    """
    Returns job identifier
    """
    logger.info(f"Printing options: {printing_options}")

    if (innohassle_user_id, filename) in tempfiles:
        printer = printing_repository.get_printer(printer_cups_name)
        if not printer:
            raise HTTPException(400, "No such printer")
        full_path = tempfiles[(innohassle_user_id, filename)].name
        job_id = printing_repository.print_file(printer, full_path, "job", printing_options)
        logger.info(f"Job {job_id} has started")
        os.unlink(full_path)
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
        full_path = tempfiles[(innohassle_user_id, filename)].name
        os.unlink(full_path)
        del tempfiles[(innohassle_user_id, filename)]
    else:
        raise HTTPException(404, "No such file")


@router.post("/debug/getPrinterAttributes")
async def get_printer_attributes(
    _innohassle_user_id: USER_AUTH,
    printer_cups_name: str,
) -> dict[str, Any]:
    cups_server = printing_repository.server
    return cups_server.getPrinterAttributes(printer_cups_name)


@router.post("/debug/createJob")
async def create_job(
    _innohassle_user_id: USER_AUTH,
    printer: str,
    file_upload_file: UploadFile,
) -> int:
    cups_server = printing_repository.server
    with tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf") as f:
        f.write(await file_upload_file.read())
        f.flush()
        job_id = cups_server.createJob(printer, f.name, {})
        logger.info(f"Job {job_id} has started")
        return job_id


@router.post("/debug/getJobAttributes")
async def get_job_attributes(
    _innohassle_user_id: USER_AUTH,
    job_id: int,
) -> dict[str, Any]:
    cups_server = printing_repository.server
    return cups_server.getJobAttributes(job_id)
