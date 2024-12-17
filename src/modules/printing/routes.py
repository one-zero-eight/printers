import os
import pathlib
import tempfile

from fastapi import APIRouter, UploadFile
from fastapi.exceptions import HTTPException
from starlette.responses import FileResponse

from src.modules.converting.repository import converting_repository
from src.modules.printing.repository import PrintingOptions, printing_repository

router = APIRouter(prefix="/print", tags=["Print"])


@router.get("/job_status")
async def job_status(job_id: int) -> str:
    """
    Returns the status of a job
    """

    return printing_repository.get_job_status(job_id)


tempfiles = {}
dir_for_temp = os.getcwd() + "/tmp"


@router.post("/prepare", responses={400: {"description": "Unsupported format"}})
async def prepare_printing(file: UploadFile) -> str:
    """
    Convert a file to pdf and return the path to the converted file
    """

    ext = file.filename[file.filename.rfind(".") :]
    if ext == ".pdf":
        f = tempfile.NamedTemporaryFile(dir=dir_for_temp, suffix=".pdf")
        f.write(await file.read())
        tempfiles[f.name] = f
        return f.name
    elif ext in [".doc", ".docx", ".png", ".txt", ".jpg", ".md", ".bmp", ".xlsx", ".xls", ".odt", ".ods"]:
        with (
            tempfile.NamedTemporaryFile(dir=dir_for_temp, suffix=ext) as in_f,
            tempfile.NamedTemporaryFile(dir=dir_for_temp, suffix=".pdf", delete=False) as out_f,
        ):
            in_f.write(await file.read())
            in_f.flush()
            converting_repository.any2pdf(in_f.name, out_f.name)
            in_f.close()
            tempfiles[out_f.name] = out_f
        return out_f.name
    else:
        raise HTTPException(400, "Unsupported format")


@router.post("/print", responses={404: {"description": "No such file"}})
def actual_print(filename: str, printer_name: str, printing_options: PrintingOptions = PrintingOptions()) -> int:
    """
    Returns job identifier
    """

    if filename in tempfiles:
        job_id = printing_repository.print_file(printer_name, filename, "job", printing_options)
        os.unlink(filename)
        del tempfiles[filename]
        return job_id
    else:
        raise HTTPException(404, "No such file")


@router.get("/get_file", responses={404: {"description": "No such file"}})
def get_file(filename: str) -> FileResponse:
    if filename in tempfiles:
        short_name = pathlib.Path(filename).name
        return FileResponse(filename, headers={"Content-Disposition": f"attachment; filename={short_name}"})
    else:
        raise HTTPException(404, "No such file")
