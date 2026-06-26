from fastapi import Request
from fastapi.responses import JSONResponse
from app.configs.settings import settings

N8N_SECRET_TOKEN = settings.N8N_SECRET_TOKEN

async def verify_n8n_request(request: Request, call_next):
    if request.url.path != "/":
        token = request.headers.get("X-N8N-KEY")
        
        if token != N8N_SECRET_TOKEN:
            return JSONResponse(
                status_code=403,
                content={"detail": "Forbidden: Only registered n8n instances can access this engine."}
            )

    response = await call_next(request)
    return response