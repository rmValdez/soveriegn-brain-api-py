from fastapi import APIRouter
from src.app.modules.chat import router as chat_router

api_router = APIRouter()
api_router.include_router(chat_router.router, prefix="/chat", tags=["chat"])

@api_router.get("/health")
async def health_check():
    return {"status": "ok"}
