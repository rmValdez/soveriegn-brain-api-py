from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.sessions.models import Session, Message

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, title: Optional[str] = None) -> Session:
        session = Session(title=title)
        self.db.add(session)
        await self.db.commit()
        return await self.get_session(session.id)

    async def get_session(self, session_id: str) -> Optional[Session]:
        stmt = select(Session).where(Session.id == session_id).options(selectinload(Session.messages))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_sessions(self) -> List[Session]:
        stmt = select(Session).order_by(Session.created_at.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_session(self, session_id: str) -> bool:
        session = await self.get_session(session_id)
        if session:
            await self.db.delete(session)
            await self.db.commit()
            return True
        return False

    async def add_message(self, session_id: str, role: str, content: str) -> Message:
        message = Message(session_id=session_id, role=role, content=content)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        
        # Update session updated_at
        session = await self.get_session(session_id)
        if session and session.title is None and role == "user":
            # Auto-title based on first message
            session.title = content[:30] + "..." if len(content) > 30 else content
            await self.db.commit()

        return message
