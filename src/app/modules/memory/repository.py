from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from .models import Memory
from .schemas import MemoryCreate, MemoryUpdate

class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, obj_in: MemoryCreate) -> Memory:
        db_obj = Memory(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
        
    async def get_by_id(self, id: str) -> Optional[Memory]:
        result = await self.session.execute(select(Memory).where(Memory.id == id))
        return result.scalars().first()
        
    async def get_all_by_user(self, user_id: str) -> List[Memory]:
        result = await self.session.execute(select(Memory).where(Memory.user_id == user_id))
        return list(result.scalars().all())
        
    async def update(self, db_obj: Memory, obj_in: MemoryUpdate) -> Memory:
        update_data = obj_in.model_dump(exclude_unset=True)
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
