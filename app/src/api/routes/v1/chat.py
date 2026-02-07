from fastapi import APIRouter, Depends

from config.settings import get_settings
from core.services.chat_service import ChatService
from api.routes.v1.models.schemas import ChatRequest, ChatResponse
from utils.logger import setup_logger

logger = setup_logger("src.api.routes.v1.chat")
router = APIRouter(prefix="/chat")

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, settings = Depends(get_settings)):
    try:
        logger.info(f"Chat request: {request}")
        chat_service = ChatService()
        response = await chat_service.process_message(
            message=request.message,
            model=request.model,
            model_provider=request.model_provider,
            session_id=request.session_id
        )
        logger.info(f"Chat response: {response}")
        return ChatResponse(response=response) 
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise e
