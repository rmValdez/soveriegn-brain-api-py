from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.modules.brain.interfaces import LLMProvider
from app.infrastructure.ollama.adapter import OllamaAdapter
from .schemas import MemoryCreate, MemoryUpdate, MemoryResponse, MemorySearchRequest
from .repository import MemoryRepository
from .models import MemoryType

class MemoryService:
    def __init__(self, session: AsyncSession, llm: Optional[LLMProvider] = None):
        self.repository = MemoryRepository(session)
        self.llm = llm or OllamaAdapter()
        
    async def create_memory(self, memory: MemoryCreate) -> MemoryResponse:
        embedding = await self.llm.get_embedding(memory.content)
        db_memory = await self.repository.create(memory, embedding=embedding if embedding else None)
        return MemoryResponse.model_validate(db_memory)
        
    async def get_memory(self, id: str) -> Optional[MemoryResponse]:
        db_memory = await self.repository.get_by_id(id)
        if db_memory:
            return MemoryResponse.model_validate(db_memory)
        return None
        
    async def get_user_memories(self, user_id: str) -> List[MemoryResponse]:
        db_memories = await self.repository.get_all_by_user(user_id)
        return [MemoryResponse.model_validate(mem) for mem in db_memories]

    async def search_memories(self, request: MemorySearchRequest) -> List[MemoryResponse]:
        query_vector = await self.llm.get_embedding(request.query)
        db_memories = await self.repository.search_hybrid(
            query=request.query,
            query_vector=query_vector if query_vector else None,
            user_id=request.user_id,
            memory_type=request.type,
            limit=request.limit
        )
        return [MemoryResponse.model_validate(mem) for mem in db_memories]
        
    async def update_memory(self, id: str, memory_update: MemoryUpdate) -> Optional[MemoryResponse]:
        db_memory = await self.repository.get_by_id(id)
        if not db_memory:
            return None
        embedding = None
        if memory_update.content:
            embedding = await self.llm.get_embedding(memory_update.content)
        updated_memory = await self.repository.update(db_memory, memory_update, embedding=embedding)
        return MemoryResponse.model_validate(updated_memory)
        
    async def delete_memory(self, id: str) -> bool:
        return await self.repository.delete(id)
