from fastapi import APIRouter
from api.routes.v1.chat import router as chat_router

api_router = APIRouter()
api_router.include_router(chat_router, prefix="/v1")