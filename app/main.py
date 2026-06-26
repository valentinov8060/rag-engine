from fastapi import FastAPI
from app.middleware.security import verify_n8n_request
from app.controllers import documents_controller, chats_controller

app = FastAPI(
    title="RAG Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.middleware("http")(verify_n8n_request)

app.include_router(documents_controller.router)
app.include_router(chats_controller.router)

@app.get("/")
def root_endpoint():
    return {"status": "online"}