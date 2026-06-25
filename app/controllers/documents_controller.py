from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Annotated
from app.configs.logger import logger
from app.validators.documents_validation import validate_ingest_request, validate_remove_document
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
    source_id: Annotated[str, Form(..., description="The source ID of the document.")],
    file_name: Annotated[str, Form(..., description="The name of the document file.")],
    file: Annotated[UploadFile, File(..., description="The document file to be ingested. Supported formats: .pdf")], 
):
    try:
        validate_ingest_request(source_id=source_id, file_name=file_name, file=file)

        total_chunks = await documents_service.post_ingest_document(source_id=source_id, file_name=file_name, file=file)
        logger.info(f"Successfully responded to post documents/ingest request. With file: {file_name}, source_id: {source_id} and total chunks created: {total_chunks}")
        return {
            "status": "success",
            "message": f"The '{file_name}' document was successfully processed to Vector DB.",
            "data": {
                "source_id": source_id,
                "total_chunks_created": total_chunks
            }
        }
    except Exception as e:
        logger.error(f"Failed to respond to post documents/ingest request. Error occurred while processing document: {str(e)}")
        raise HTTPException(500, detail=f"Failed to process document: {str(e)}")


@router.get(
    "/list/{source_id}",
    summary="Get a list of unique documents belonging to a user",
    description="This endpoint is used to retrieve all PDF file names ever uploaded by a user based on their Telegram Chat ID"
)
async def list(source_id: str):
    try:
        documents = await documents_service.get_list_user_documents(source_id=source_id)
        logger.info(f"Successfully responded to get documents/list request. With source_id: {source_id}")
        return {
            "status": "success",
            "message": f"Found {len(documents)} unique documents for user {source_id}",
            "data": {
                "source_id": source_id,
                "documents": documents
            }
        }
    except Exception as e:
        logger.error(f"Failed to respond to get documents/list request. Error occurred while processing document: {str(e)}")
        raise HTTPException(500, detail=f"Failed to load document list: {str(e)}")


@router.delete(
    "/remove",
    summary="Remove a document from the vector database",
    description="This endpoint is used to remove a document from the vector database based on the source ID and file name"
)
async def remove_document(source_id: str, file_name: str):
    try:
        validate_remove_document(source_id=source_id, file_name=file_name)

        await documents_service.delete_user_document(source_id=source_id, file_name=file_name)
        logger.info(f"Successfully responded to delete documents/remove request. With file: {file_name}, source_id: {source_id}")
        return {
            "status": "success",
            "message": f"Document '{file_name}' has been permanently deleted."
        }
    except Exception as e:
        logger.error(f"Failed to respond to delete documents/remove request. Error occurred while processing document: {str(e)}")
        raise HTTPException(500, detail=f"Failed to delete document: {str(e)}")
