from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.configs.logger import logger
from app.services.chats_service import ChatsService
from app.validators.chats_validation import validate_post_chat_request

router = APIRouter(
    prefix="/api/v1/chats",
    tags=["Chats"]
)

chats_service = ChatsService()

class QuestionRequestBody(BaseModel):
    source_id: str
    question: str

@router.post(
    "/question",
    summary="Chat with the RAG Engine",
    description="This endpoint allows users to ask questions based on their uploaded documents."
)
async def question(
    payload: QuestionRequestBody
):
    try:
        validate_post_chat_request(source_id=payload.source_id, question=payload.question)

        answer = await chats_service.post_chat_question(
            source_id=payload.source_id,
            question=payload.question
        )
        logger.info(f"Successfully responded to post chats/question request. With source_id: {payload.source_id} and question: {payload.question}")
        return {
            "status": "success",
            "message": f"Successfully processed the question for user {payload.source_id}",
            "data": {
                "source_id": payload.source_id,
                "answer": answer
            }
        }
    except Exception as e:
        logger.error(f"Failed to respond to post chats/question request. Error occurred while processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")