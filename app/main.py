from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.merge import router as merge_router
app = FastAPI(
    title="DocFusion API",
    description = "PDF and Word document merger API",
    version = "1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(merge_router)

@app.get("/")
def home():
    return{
        "message" : "Welcome to DocFusion API"
    }