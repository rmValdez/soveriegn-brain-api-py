from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .schemas import MemoryCreate, MemoryUpdate, MemoryResponse
from .repository import MemoryRepository

class MemoryService:
    def __init__(self, session: AsyncSession):
        self.repository = MemoryRepository(session)
        
    async def create_memory(self, memory: MemoryCreate) -> MemoryResponse:
        db_memory = await self.repository.create(memory)
        return MemoryResponse.model_validate(db_memory)
        
    async def get_memory(self, id: str) -> Optional[MemoryResponse]:
        db_memory = await self.repository.get_by_id(id)
        if db_memory:
            return MemoryResponse.model_validate(db_memory)
        return None
        
    async def get_user_memories(self, user_id: str) -> List[MemoryResponse]:
        db_memories = await self.repository.get_all_by_user(user_id)
        return [MemoryResponse.model_validate(mem) for mem in db_memories]
        
    async def update_memory(self, id: str, memory_update: MemoryUpdate) -> Optional[MemoryResponse]:
        db_memory = await self.repository.get_by_id(id)
        if not db_memory:
            return None
        updated_memory = await self.repository.update(db_memory, memory_update)
        return MemoryResponse.model_validate(updated_memory)
        
    async def delete_memory(self, id: str) -> bool:
        return await self.repository.delete(id)
