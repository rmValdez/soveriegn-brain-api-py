from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.modules.sessions.models import Session, Message, ConversationSummary

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(self, title: Optional[str] = None, user_id: Optional[str] = None) -> Session:
        session = Session(title=title, user_id=user_id)
        self.db.add(session)
        await self.db.commit()
        return await self.get_session(session.id)

    async def get_session(self, session_id: str) -> Optional[Session]:
        stmt = select(Session).where(Session.id == session_id).options(
            selectinload(Session.messages),
            selectinload(Session.summary)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_sessions(self, user_id: Optional[str] = None) -> List[Session]:
        stmt = select(Session)
        if user_id:
            stmt = stmt.where(Session.user_id == user_id)
        stmt = stmt.order_by(Session.created_at.desc())
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

    async def get_summary(self, session_id: str) -> Optional[ConversationSummary]:
        stmt = select(ConversationSummary).where(ConversationSummary.session_id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_summary(
        self,
        session_id: str,
        summary: str,
        last_message_id: Optional[str] = None,
        tokens_count: Optional[int] = None
    ) -> ConversationSummary:
        existing = await self.get_summary(session_id)
        if existing:
            existing.summary = summary
            existing.last_message_id = last_message_id
            existing.tokens_count = tokens_count
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            new_summary = ConversationSummary(
                session_id=session_id,
                summary=summary,
                last_message_id=last_message_id,
                tokens_count=tokens_count
            )
            self.db.add(new_summary)
            await self.db.commit()
            await self.db.refresh(new_summary)
            return new_summary
