from fastapi import FastAPI

app = FastAPI(
    title="DocFusion API",
    description = "PDF and Word document merger API",
    version = "1.0.0"
)

@app.get("/")
def home():
    return{
        "message" : "Welcome to DocFusion API"
    }