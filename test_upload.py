from fastapi import FastAPI, UploadFile, File

app = FastAPI()


@app.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...)
):
    return {
        "filenames": [file.filename for file in files]
    }