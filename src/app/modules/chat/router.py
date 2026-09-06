from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.chat.schemas import ChatRequest, ChatResponse
from app.modules.brain.orchestrator import BrainOrchestrator

router = APIRouter(prefix="/chat", tags=["Chat"])
orchestrator = BrainOrchestrator()

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        response, session_id = await orchestrator.process_message(request.message, db, request.session_id, user_id=request.user_id)
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def chat_stream(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Stream endpoint does not easily return headers/JSON with session_id initially
    # In a real app, you might send a custom event first with the session_id
    return StreamingResponse(
        orchestrator.process_message_stream(request.message, db, request.session_id, user_id=request.user_id),
        media_type="text/event-stream"
    )
