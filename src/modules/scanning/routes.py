import asyncio
import tempfile
from pathlib import Path

import PyPDF2
from fastapi import APIRouter, Body, HTTPException
from starlette.responses import FileResponse, Response

from src.api.dependencies import USER_AUTH
from src.config import settings
from src.config_schema import Scanner
from src.modules.scanning.entity_models import ScannerStatus, ScanningOptions, ScanningResult
from src.modules.scanning.repository import scanning_repository
from src.modules.scanning.tools.auto_crop import autocrop_pdf_bytes
from src.modules.scanning.tools.document_merger import merge_documents

router = APIRouter(prefix="/scan", tags=["Scan"])


@router.get("/get_scanners")
async def get_scanners(_innohassle_user_id: USER_AUTH) -> list[Scanner]:
    return settings.api.scanners_list


@router.get("/get_file", responses={404: {"description": "No such file"}})
def get_file(filename: str, innohassle_user_id: USER_AUTH) -> FileResponse:
    if (innohassle_user_id, filename) in scanning_repository.tempfiles:
        return FileResponse(
            scanning_repository.get_tempfile_path(innohassle_user_id, filename),
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    else:
        raise HTTPException(404, "No such file. It was removed from our servers due to expiration")


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
    scanning_repository.store_job_options(innohassle_user_id, job_id, scanning_options)
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
    await scanning_repository.delete_printer_scan_job(scanner, job_id)


@router.post("/manual/wait_and_merge")
async def manual_wait_and_merge(
    innohassle_user_id: USER_AUTH,
    scanner_name: str,
    job_id: str,
    prev_filename: str | None = None,
) -> ScanningResult | None:
    if prev_filename and (innohassle_user_id, prev_filename) not in scanning_repository.tempfiles:
        raise HTTPException(404, "No such scan")

    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")

    document = await scanning_repository.fetch_scan_one(scanner, job_id)
    if not document:
        raise HTTPException(404, "The scan document was not found")
    if scanning_repository.retrieve_job_options(innohassle_user_id, job_id).crop == "true":
        document = autocrop_pdf_bytes(document)

    if prev_filename:
        tempfile_f = scanning_repository.retrieve_tempfile(innohassle_user_id, prev_filename)
        out_f = await asyncio.to_thread(merge_documents, document, tempfile_f)
        scanning_repository.remove_tempfile(innohassle_user_id, prev_filename)
        scanning_repository.store_tempfile(innohassle_user_id, out_f)
    else:
        with tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f:
            out_f.write(document)
            out_f.flush()
            scanning_repository.store_tempfile(innohassle_user_id, out_f)
    return ScanningResult(filename=Path(out_f.name).name, page_count=len(PyPDF2.PdfReader(out_f.name).pages))


@router.post("/manual/remove_last_page")
async def manual_remove_last_page(
    filename: str,
    innohassle_user_id: USER_AUTH,
) -> ScanningResult:
    if (innohassle_user_id, filename) not in scanning_repository.tempfiles:
        raise HTTPException(404, "No such scan")

    tempfile_f = scanning_repository.retrieve_tempfile(innohassle_user_id, filename)
    infile = PyPDF2.PdfReader(tempfile_f.name)
    with tempfile.NamedTemporaryFile(dir=settings.api.temp_dir, suffix=".pdf", delete=False) as out_f:
        outfile = PyPDF2.PdfWriter(out_f)
        for page in infile.pages[:-1]:
            outfile.add_page(page)
        outfile.write(out_f)
        scanning_repository.store_tempfile(innohassle_user_id, out_f)
    scanning_repository.remove_tempfile(innohassle_user_id, filename)
    return ScanningResult(filename=Path(out_f.name).name, page_count=len(PyPDF2.PdfReader(out_f.name).pages))


@router.post("/manual/delete_file")
async def manual_delete_file(
    filename: str,
    innohassle_user_id: USER_AUTH,
):
    if (innohassle_user_id, filename) not in scanning_repository.tempfiles:
        raise HTTPException(404, "No such scan")

    scanning_repository.remove_tempfile(innohassle_user_id, filename)


@router.get("/debug/get_scanner_capabilities")
async def get_scanner_capabilities_debug(
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
) -> ScannerStatus:
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    status = await scanning_repository.get_scanner_status(scanner)
    return status


@router.post("/debug/scan_one_page")
async def scan_one_page(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
    scanning_options: ScanningOptions,
):
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    document = await scanning_repository.scan_one_page_debug(scanner, scanning_options)
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


@router.get("/debug/fetch_scanned_document")
async def fetch_scanned_document_debug(
    _innohassle_user_id: USER_AUTH,
    scanner_name: str,
    job_id: str,
):
    scanner = scanning_repository.get_scanner(scanner_name)
    if not scanner:
        raise HTTPException(404, "No such scanner")
    response = await scanning_repository.fetch_scanned_document(scanner, job_id)
    return Response(response, media_type="application/pdf")
