from fastapi import APIRouter

from config.settings import get_settings
from api.routes.v1.chat import router as chat_router

api_router = APIRouter()
settings = get_settings()
api_router.include_router(chat_router, prefix=settings.API_V1_STR)