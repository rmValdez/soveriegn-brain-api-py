from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from .schemas import MemoryCreate, MemoryUpdate, MemoryResponse, MemorySearchRequest
from .service import MemoryService

router = APIRouter(prefix="/api/v1/memories", tags=["memories"])

def get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    return MemoryService(db)

@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory: MemoryCreate,
    service: MemoryService = Depends(get_memory_service)
):
    return await service.create_memory(memory)

@router.post("/search", response_model=List[MemoryResponse])
async def search_memories(
    search_req: MemorySearchRequest,
    service: MemoryService = Depends(get_memory_service)
):
    return await service.search_memories(search_req)

@router.get("/user/{user_id}", response_model=List[MemoryResponse])
async def get_user_memories(
    user_id: str,
    service: MemoryService = Depends(get_memory_service)
):
    return await service.get_user_memories(user_id)

@router.get("/{id}", response_model=MemoryResponse)
async def get_memory(
    id: str,
    service: MemoryService = Depends(get_memory_service)
):
    memory = await service.get_memory(id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.put("/{id}", response_model=MemoryResponse)
async def update_memory(
    id: str,
    memory_update: MemoryUpdate,
    service: MemoryService = Depends(get_memory_service)
):
    memory = await service.update_memory(id, memory_update)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    id: str,
    service: MemoryService = Depends(get_memory_service)
):
    success = await service.delete_memory(id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
