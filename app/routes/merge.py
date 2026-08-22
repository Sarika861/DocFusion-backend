import os
import tempfile
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from app.services.pdf_merger import merge_pdfs


router = APIRouter(
    prefix="/api",
    tags=["Document Merger"]
)


MAX_FILES = 10
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/merge-pdfs")
async def merge_pdf_files(
    files: Annotated[list[UploadFile], File(...)]
):

    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least 2 PDF files."
        )

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"You can upload maximum {MAX_FILES} files."
        )

    for file in files:

        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF file."
            )

    temp_files = []

    try:

        for file in files:

            content = await file.read()

            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is larger than 10 MB."
                )

            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            )

            temp_file.write(content)
            temp_file.close()

            temp_files.append(temp_file.name)

        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        )

        output_path = output_file.name
        output_file.close()

        merge_pdfs(
            temp_files,
            output_path
        )

        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename="merged_document.pdf"
        )

    finally:

        for file_path in temp_files:

            if os.path.exists(file_path):
                os.remove(file_path)