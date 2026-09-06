from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.sessions.repository import SessionRepository
from app.modules.sessions.schemas import SessionRead, SessionListRead
from fastapi import HTTPException

class SessionService:
    def __init__(self, db: AsyncSession):
        self.repo = SessionRepository(db)

    async def create_session(self, title: Optional[str] = None, user_id: Optional[str] = None) -> SessionRead:
        session = await self.repo.create_session(title, user_id)
        return SessionRead.model_validate(session)

    async def get_session(self, session_id: str) -> SessionRead:
        session = await self.repo.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return SessionRead.model_validate(session)

    async def list_sessions(self, user_id: Optional[str] = None) -> List[SessionListRead]:
        sessions = await self.repo.list_sessions(user_id)
        return [SessionListRead.model_validate(s) for s in sessions]

    async def delete_session(self, session_id: str) -> bool:
        deleted = await self.repo.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return deleted
