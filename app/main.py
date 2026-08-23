import io
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pypdf import PdfReader, PdfWriter


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="DocFusion PDF Merger API",
    description="API for merging multiple PDF documents",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROOT ROUTE
# =========================================================

@app.get("/")
async def root():
    return {
        "message": "DocFusion Backend is running",
        "status": "success"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }


# =========================================================
# MERGE PDFS
# =========================================================

@app.post("/api/merge-pdfs")
async def merge_pdfs(
    files: List[UploadFile] = File(...)
):

    # -----------------------------------------------------
    # Check number of files
    # -----------------------------------------------------

    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="Please select at least 2 PDF files."
        )


    writer = PdfWriter()

    try:

        # -------------------------------------------------
        # Process every uploaded PDF
        # -------------------------------------------------

        for file in files:

            # Check filename
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="A file has no filename."
                )


            # Check extension
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is not a PDF file."
                )


            # Read file
            contents = await file.read()


            # Check empty file
            if not contents:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file.filename} is empty."
                )


            # -------------------------------------------------
            # Validate PDF
            # -------------------------------------------------

            try:

                pdf_stream = io.BytesIO(contents)

                reader = PdfReader(pdf_stream)

                # Check if PDF is encrypted
                if reader.is_encrypted:

                    try:
                        reader.decrypt("")
                    except Exception:
                        raise HTTPException(
                            status_code=400,
                            detail=(
                                f"{file.filename} is password protected. "
                                "Please upload an unlocked PDF."
                            )
                        )


                # Check pages
                if len(reader.pages) == 0:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{file.filename} contains no pages."
                    )


                # -------------------------------------------------
                # Add pages to writer
                # -------------------------------------------------

                for page in reader.pages:
                    writer.add_page(page)


            except HTTPException:
                raise

            except Exception as pdf_error:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Could not read {file.filename}: "
                        f"{str(pdf_error)}"
                    )
                )


        # -----------------------------------------------------
        # Create merged PDF in memory
        # -----------------------------------------------------

        output_stream = io.BytesIO()

        writer.write(output_stream)

        writer.close()

        output_stream.seek(0)


        # Get final PDF bytes
        merged_pdf = output_stream.getvalue()


        # -----------------------------------------------------
        # Make sure output is not empty
        # -----------------------------------------------------

        if not merged_pdf:

            raise HTTPException(
                status_code=500,
                detail="Merged PDF is empty."
            )


        print(
            f"Successfully merged {len(files)} PDFs "
            f"({len(merged_pdf)} bytes)"
        )


        # -----------------------------------------------------
        # Return PDF
        # -----------------------------------------------------

        return Response(

            content=merged_pdf,

            media_type="application/pdf",

            headers={

                # inline = browser can preview PDF
                "Content-Disposition":
                    "inline; filename=merged.pdf",

                # Prevent caching old PDF
                "Cache-Control":
                    "no-cache, no-store, must-revalidate",

                "Pragma":
                    "no-cache",

                "Expires":
                    "0",

                # Tell browser exact size
                "Content-Length":
                    str(len(merged_pdf))
            }
        )


    except HTTPException:
        raise


    except Exception as e:

        print(
            f"Unexpected merge error: {str(e)}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Failed to merge PDFs: {str(e)}"
        )


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )