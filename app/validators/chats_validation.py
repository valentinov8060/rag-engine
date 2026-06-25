from fastapi import HTTPException

def validate_post_chat_request(source_id: str = None, question: str = None):
    if not source_id or not source_id.strip():
        raise HTTPException(
            status_code=400,
            detail="The source ID is empty."
        )
        
    if not question or not question.strip():
        raise HTTPException(
            status_code=400,
            detail="The question content is empty."
        )