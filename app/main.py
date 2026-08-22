import io
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pypdf import PdfWriter

app = FastAPI()

# 1. Enable CORS for Angular (http://localhost:4200)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/merge-pdfs")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="At least 2 PDF files are required.")

    merger = PdfWriter()

    try:
        for file in files:
            # Validate file extension or MIME type
            if not file.filename.endswith(".pdf"):
                continue

            # Read stream into memory buffer
            contents = await file.read()
            pdf_stream = io.BytesIO(contents)
            
            # Append to merger stream
            merger.append(pdf_stream)

        # Output the merged PDF to an in-memory buffer
        output_stream = io.BytesIO()
        merger.write(output_stream)
        merger.close()
        
        output_stream.seek(0)

        # Return file response with proper headers
        return Response(
            content=output_stream.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=merged.pdf"
            }
        )

    except Exception as e:
        print(f"Merge Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to merge PDFs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)