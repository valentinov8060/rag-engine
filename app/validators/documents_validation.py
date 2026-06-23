import os
from fastapi import HTTPException, UploadFile

ALLOWED_EXTENSIONS = [".pdf"]

def validate_ingest_request(file: UploadFile, source_id: str = None):
    # File validation
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="The file has no name."
        )

    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"The file format '{file_extension}' is not supported. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}."
        )

    # Source ID validation
    if not source_id:
        raise HTTPException(
            status_code=400,
            detail="The source ID is empty."
        )