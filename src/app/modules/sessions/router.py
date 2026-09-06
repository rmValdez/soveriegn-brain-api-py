from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.sessions.schemas import SessionCreate, SessionRead, SessionListRead
from app.modules.sessions.service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("", response_model=SessionRead, status_code=201)
async def create_session(body: SessionCreate = SessionCreate(), db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    return await service.create_session(body.title)

@router.get("", response_model=List[SessionListRead])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    return await service.list_sessions()

@router.get("/{session_id}", response_model=SessionRead)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    return await service.get_session(session_id)

@router.delete("/{session_id}", status_code=204)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    service = SessionService(db)
    await service.delete_session(session_id)
