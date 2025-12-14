import asyncio
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any

import PyPDF2
from fastapi import APIRouter, Body, HTTPException
from starlette.responses import FileResponse, Response

from src.api.dependencies import USER_AUTH
from src.config import settings
from src.config_schema import Scanner
from src.modules.scanning.entity_models import ScanningOptions, ScanningResult
from src.modules.scanning.repository import scanning_repository
from src.modules.scanning.tools.auto_crop import autocrop_pdf_bytes

router = APIRouter(prefix="/scan", tags=["Scan"])
tempfiles: dict[tuple[str, str], Any] = {}
job_options: dict[tuple[str, str], ScanningOptions] = {}


@router.get("/get_scanners")
async def get_scanners(_innohassle_user_id: USER_AUTH) -> list[Scanner]:
    return settings.api.scanners_list


@router.get("/get_file", responses={404: {"description": "No such file"}})
def get_file(filename: str, innohassle_user_id: USER_AUTH) -> FileResponse:
    if (innohassle_user_id, filename) in tempfiles:
        full_path = tempfiles[(innohassle_user_id, filename)].name
        return FileResponse(full_path, headers={"Content-Disposition": f"attachment; filename={filename}"})
    else:
        raise HTTPException(404, "No such file")


@router.post("/manual/start_scan")
async def manual_start_scan(
    innohassle_user_id: USER_AUTH,
    scanner_name: str,
    scanning_options: ScanningOptions = Body(ScanningOptions(), embed=True),
) -> str | None:
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    job_id = await scanning_repository.start_scan_one(scanner, scanning_options)
    if not job_id:
        raise HTTPException(503, "Scanner is busy or not available")
    job_options[(innohassle_user_id, job_id)] = scanning_options
    return job_id


@router.post("/manual/cancel_scan")
async def manual_cancel_scan(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
    job_id: str,
) -> None:
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    await scanning_repository._delete_printer_scan_job(scanner, job_id)


@router.post("/manual/wait_and_merge")
async def manual_wait_and_merge(
    innohassle_user_id: USER_AUTH,
    scanner_name: str,
    job_id: str,
    prev_filename: str | None = None,
) -> ScanningResult:
    if prev_filename and (innohassle_user_id, prev_filename) not in tempfiles:
        raise HTTPException(404, "No such tempfile")

    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")

    document = await scanning_repository.fetch_scan_one(scanner, job_id)
    if not document:
        raise HTTPException(503, "Scanner is busy or not available")
    if job_options[(innohassle_user_id, job_id)].crop == "true":
        document = autocrop_pdf_bytes(document)
        del job_options[(innohassle_user_id, job_id)]

    if prev_filename:
        # Merge documents tempfile_f and document to out_f using PyPDF2
        tempfile_f = tempfiles[(innohassle_user_id, prev_filename)]

        def merge_documents(document: bytes, tempfile_f):
            with tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f:
                merger = PyPDF2.PdfMerger()
                merger.append(tempfile_f.name)
                merger.append(BytesIO(document))
                merger.write(out_f.name)
                merger.close()
                return out_f

        out_f = await asyncio.to_thread(merge_documents, document, tempfile_f)
        # Delete tempfile_f
        tempfile_f.close()
        os.unlink(tempfile_f.name)
        tempfiles.pop((innohassle_user_id, prev_filename))
        # Add out_f to tempfiles
        tempfiles[(innohassle_user_id, Path(out_f.name).name)] = out_f
    else:
        # Save to tempfile
        with tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f:
            out_f.write(document)
            out_f.flush()
            tempfiles[(innohassle_user_id, Path(out_f.name).name)] = out_f
    return ScanningResult(filename=Path(out_f.name).name, page_count=len(PyPDF2.PdfReader(out_f.name).pages))


@router.post("/manual/remove_last_page")
async def manual_remove_last_page(
    filename: str,
    innohassle_user_id: USER_AUTH,
) -> ScanningResult:
    if (innohassle_user_id, filename) not in tempfiles:
        raise HTTPException(404, "No such tempfile")

    tempfile_f = tempfiles[(innohassle_user_id, filename)]
    infile = PyPDF2.PdfReader(tempfile_f.name)
    with tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f:
        outfile = PyPDF2.PdfWriter(out_f)
        for page in infile.pages[:-1]:
            outfile.add_page(page)
        outfile.write(out_f)
        tempfiles[(innohassle_user_id, Path(out_f.name).name)] = out_f
    # Remove previous tempfile
    tempfile_f.close()
    os.unlink(tempfile_f.name)
    tempfiles.pop((innohassle_user_id, filename))
    return ScanningResult(filename=Path(out_f.name).name, page_count=len(PyPDF2.PdfReader(out_f.name).pages))


@router.post("/manual/delete_file")
async def manual_delete_file(
    filename: str,
    innohassle_user_id: USER_AUTH,
):
    if (innohassle_user_id, filename) not in tempfiles:
        raise HTTPException(404, "No such tempfile")

    tempfile_f = tempfiles[(innohassle_user_id, filename)]
    tempfile_f.close()
    os.unlink(tempfile_f.name)
    tempfiles.pop((innohassle_user_id, filename))


@router.get("/debug/get_scanner_capabilities")
async def get_scanner_capabilities(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
):
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    response = await scanning_repository.get_scanner_capabilities(scanner)
    return Response(response, media_type="application/xml")


@router.get("/debug/get_scanner_status")
async def get_scanner_status(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
):
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    response = await scanning_repository.get_scanner_status(scanner)
    return Response(response, media_type="application/xml")


@router.post("/debug/scan_one_page")
async def scan_one_page(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
    scanning_options: ScanningOptions,
):
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    document = await scanning_repository.scan_one_page(scanner, scanning_options)
    if not document:
        raise HTTPException(503, "Scanner is busy or not available")
    return Response(document, media_type="application/pdf")


@router.post("/debug/start_scan")
async def start_scan(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
    options: ScanningOptions,
) -> str | None:
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    return await scanning_repository.start_scan_one(scanner, options)


@router.post("/debug/delete_printer_scan_job")
async def delete_printer_scan_job(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
    job_id: str,
):
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    await scanning_repository._delete_printer_scan_job(scanner, job_id)


@router.get("/debug/fetch_scanned_document")
async def fetch_scanned_document(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
    job_id: str,
):
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    response = await scanning_repository._fetch_scanned_document(scanner, job_id)
    return Response(response, media_type="application/pdf")
