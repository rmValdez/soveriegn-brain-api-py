import pytest
from unittest.mock import AsyncMock, MagicMock
from app.modules.memory.schemas import MemoryCreate, MemorySearchRequest
from app.modules.memory.models import Memory, MemoryType
from app.modules.brain.context import ContextEngine

@pytest.mark.asyncio
async def test_memory_extraction_pattern():
    mock_llm = AsyncMock()
    mock_llm.get_embedding = AsyncMock(return_value=[0.1] * 768)
    engine = ContextEngine(llm=mock_llm)
    
    mock_db = AsyncMock()
    mock_repo = MagicMock()
    mock_repo.create = AsyncMock(return_value=Memory(id="mem-1", content="PostgreSQL is the database"))
    
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("app.modules.brain.context.MemoryRepository", lambda db: mock_repo)
        
        # Test explicit remember instruction
        extracted = await engine.extract_memory_if_instructed(
            "session-1",
            "Please remember that PostgreSQL is the database",
            mock_db
        )
        assert extracted == "PostgreSQL is the database"
        mock_repo.create.assert_called_once()
        
        # Test preference pattern
        mock_repo.create.reset_mock()
        extracted_pref = await engine.extract_memory_if_instructed(
            "session-1",
            "I prefer dark mode in all UI components",
            mock_db
        )
        assert extracted_pref == "dark mode in all UI components"
        mock_repo.create.assert_called_once()

        # Test non-memory normal message (should not extract)
        mock_repo.create.reset_mock()
        not_extracted = await engine.extract_memory_if_instructed(
            "session-1",
            "What is the weather today?",
            mock_db
        )
        assert not_extracted is None
        mock_repo.create.assert_not_called()

@pytest.mark.asyncio
async def test_context_engine_injects_long_term_memories():
    mock_llm = AsyncMock()
    mock_llm.get_embedding = AsyncMock(return_value=[0.1] * 768)
    engine = ContextEngine(llm=mock_llm)
    
    mock_db = AsyncMock()
    mock_mem = Memory(
        id="mem-1",
        user_id="default_user",
        type=MemoryType.preference,
        content="Always use TypeScript in Next.js"
    )
    
    with pytest.MonkeyPatch.context() as mp:
        mock_session_repo = MagicMock()
        mock_session_repo.get_session = AsyncMock(return_value=None)
        mp.setattr("app.modules.brain.context.SessionRepository", lambda db: mock_session_repo)
        
        mock_mem_repo = MagicMock()
        mock_mem_repo.search_hybrid = AsyncMock(return_value=[mock_mem])
        mp.setattr("app.modules.brain.context.MemoryRepository", lambda db: mock_mem_repo)
        
        context = await engine.build_context("session-1", "How do we write components?", mock_db)
        
        assert len(context) == 2
        assert "[LONG-TERM MEMORIES]" in context[0]["content"]
        assert "Always use TypeScript in Next.js" in context[0]["content"]
