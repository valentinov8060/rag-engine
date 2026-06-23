from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated
from app.configs.logger import logger
from app.validators.documents_validation import validate_ingest_request
from app.services.documents_service import DocumentsService

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)

documents_service = DocumentsService()

@router.post(
    "/ingest", 
    summary="Ingest a document into the vector database",
    description="Ingest a document into the vector database"
)
async def ingest(
    file: Annotated[UploadFile, File(..., description="The document file to be ingested. Supported formats: .pdf")], 
    source_id: Annotated[str, Form(..., description="The source ID of the document.")]
):
    logger.info("There is a request to documents/ingest.")
    validate_ingest_request(file, source_id)

    total_chunks = await documents_service.ingest_document(file=file, source_id=source_id)
    logger.info(f"Successfully responded to documents/ingest request. With file: {file.filename}, source_id: {source_id} and total chunks created: {total_chunks}")
    return {
        "status": "success",
        "message": f"The '{file.filename}' document was successfully processed to Vector DB.",
        "source_id": source_id,
        "total_chunks_created": total_chunks
    }