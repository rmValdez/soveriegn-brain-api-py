from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from .models import Memory, MemoryType
from .schemas import MemoryCreate, MemoryUpdate

class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, obj_in: MemoryCreate, embedding: Optional[List[float]] = None) -> Memory:
        data = obj_in.model_dump()
        if embedding:
            data["embedding"] = embedding
        db_obj = Memory(**data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
        
    async def get_by_id(self, id: str) -> Optional[Memory]:
        result = await self.session.execute(select(Memory).where(Memory.id == id))
        return result.scalars().first()
        
    async def get_all_by_user(self, user_id: str) -> List[Memory]:
        result = await self.session.execute(
            select(Memory).where(Memory.user_id == user_id).order_by(Memory.created_at.desc())
        )
        return list(result.scalars().all())

    async def search_hybrid(
        self,
        query: str,
        query_vector: Optional[List[float]] = None,
        user_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 5
    ) -> List[Memory]:
        stmt = select(Memory)
        if user_id:
            stmt = stmt.where(Memory.user_id == user_id)
        if memory_type:
            stmt = stmt.where(Memory.type == memory_type)

        if query_vector and len(query_vector) == 768:
            # Semantic search using pgvector cosine distance
            stmt = stmt.order_by(Memory.embedding.cosine_distance(query_vector))
        else:
            # Structured substring / keyword matching fallback
            stmt = stmt.where(
                or_(
                    Memory.content.ilike(f"%{query}%"),
                    Memory.subject.ilike(f"%{query}%")
                )
            ).order_by(Memory.created_at.desc())

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def update(self, db_obj: Memory, obj_in: MemoryUpdate, embedding: Optional[List[float]] = None) -> Memory:
        update_data = obj_in.model_dump(exclude_unset=True)
        if embedding is not None:
            update_data["embedding"] = embedding
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
        
    async def delete(self, id: str) -> bool:
        obj = await self.get_by_id(id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        return False
