import os
from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc"]

def _validate_source_id_and_file_name(source_id: str = None, file_name: str = None):
    if not source_id:
        raise HTTPException(
            status_code=400,
            detail="The source ID is empty."
        )

    if not file_name:
        raise HTTPException(
            status_code=400,
            detail="The file name is empty."
        )

def validate_ingest_request(source_id: str = None, file_name: str = None, file: UploadFile = None):
    _validate_source_id_and_file_name(source_id, file_name)

    if file and file.filename:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"The file format '{file_extension}' is not supported. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}."
            )

def validate_remove_document(source_id: str = None, file_name: str = None):
    _validate_source_id_and_file_name(source_id, file_name)