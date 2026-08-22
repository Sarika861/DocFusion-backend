from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from pypdf import PdfWriter  # Install using: pip install pypdf
import io

router = APIRouter(prefix="/api", tags=["merge"])

@router.post("/merge-pdfs")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    # 1. Validate file count
    if not files or len(files) < 2:
        raise HTTPException(
            status_code=400, 
            detail="At least 2 PDF files are required for merging."
        )

    merger = PdfWriter()

    try:
        for file in files:
            # Check for PDF extension or content type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is not a valid PDF."
                )

            # 2. Read file contents into BytesIO stream
            pdf_bytes = await file.read()
            merger.append(io.BytesIO(pdf_bytes))

        # 3. Write merged PDF into memory stream
        output_stream = io.BytesIO()
        merger.write(output_stream)
        merger.close()

        # 4. Return raw PDF bytes with correct headers
        return Response(
            content=output_stream.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=merged_document.pdf"
            }
        )

    except Exception as e:
        print(f"Error during PDF merge: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to merge PDF files: {str(e)}"
        )