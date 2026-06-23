from fastapi import FastAPI
from app.controllers import documents_controller

app = FastAPI(
    title="RAG Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.include_router(documents_controller.router)

@app.get("/")
def root_endpoint():
    return {"status": "online"}