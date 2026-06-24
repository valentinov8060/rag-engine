from fastapi import APIRouter, UploadFile, File, Form, HTTPException
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
    try:
        logger.info("There is a request to documents/ingest.")
        validate_ingest_request(file, source_id)

        total_chunks = await documents_service.post_ingest_document(file=file, source_id=source_id)
        logger.info(f"Successfully responded to documents/ingest request. With file: {file.filename}, source_id: {source_id} and total chunks created: {total_chunks}")
        return {
            "status": "success",
            "message": f"The '{file.filename}' document was successfully processed to Vector DB.",
            "data": {
                "source_id": source_id,
                "total_chunks_created": total_chunks
            }
        }
    except Exception as e:
        logger.error(f"Failed to respond to documents/ingest request. Error occurred while processing document: {str(e)}")
        raise HTTPException(500, detail=f"Failed to process document: {str(e)}")


@router.get(
    "/list/{source_id}",
    summary="Mendapatkan daftar dokumen unik milik user",
    description="Endpoint ini digunakan untuk menarik semua nama berkas PDF yang pernah diunggah oleh user berdasarkan Telegram Chat ID mereka."
)
async def list(source_id: str):
    try:
        documents = await documents_service.get_list_user_documents(source_id=source_id)
        return {
            "status": "success",
            "message": f"Ditemukan {len(documents)} dokumen unik untuk user {source_id}",
            "data": {
                "source_id": source_id,
                "documents": documents
            }
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Gagal memuat daftar dokumen: {str(e)}")
