import pytest
from unittest.mock import AsyncMock, MagicMock
from app.modules.brain.context import ContextEngine, SOVEREIGN_SYSTEM_PROMPT
from app.modules.sessions.models import Session, Message, ConversationSummary

@pytest.mark.asyncio
async def test_context_engine_empty_session():
    mock_llm = AsyncMock()
    engine = ContextEngine(llm=mock_llm)
    
    mock_db = AsyncMock()
    
    # Mock repository call
    with pytest.MonkeyPatch.context() as mp:
        mock_repo = MagicMock()
        mock_repo.get_session = AsyncMock(return_value=None)
        mp.setattr("app.modules.brain.context.SessionRepository", lambda db: mock_repo)
        
        context = await engine.build_context("session-1", "Hello Sovereign", mock_db)
        
        assert len(context) == 2
        assert context[0]["role"] == "system"
        assert context[0]["content"] == SOVEREIGN_SYSTEM_PROMPT
        assert context[1]["role"] == "user"
        assert context[1]["content"] == "Hello Sovereign"

@pytest.mark.asyncio
async def test_context_engine_short_conversation():
    mock_llm = AsyncMock()
    engine = ContextEngine(llm=mock_llm, summary_trigger_threshold=5)
    
    mock_db = AsyncMock()
    
    session = Session(id="session-1", title="Test Session")
    msg1 = Message(id="m1", session_id="session-1", role="user", content="Hi")
    msg2 = Message(id="m2", session_id="session-1", role="assistant", content="Hello!")
    session.messages = [msg1, msg2]
    
    with pytest.MonkeyPatch.context() as mp:
        mock_repo = MagicMock()
        mock_repo.get_session = AsyncMock(return_value=session)
        mp.setattr("app.modules.brain.context.SessionRepository", lambda db: mock_repo)
        
        context = await engine.build_context("session-1", "How are you?", mock_db)
        
        # System prompt + 2 historical messages + current message
        assert len(context) == 4
        assert context[0]["role"] == "system"
        assert context[1] == {"role": "user", "content": "Hi"}
        assert context[2] == {"role": "assistant", "content": "Hello!"}
        assert context[3] == {"role": "user", "content": "How are you?"}

@pytest.mark.asyncio
async def test_context_engine_injects_summary_on_long_conversation():
    mock_llm = AsyncMock()
    engine = ContextEngine(llm=mock_llm, recent_messages_limit=2, summary_trigger_threshold=3)
    
    mock_db = AsyncMock()
    
    session = Session(id="session-1", title="Long Session")
    messages = [
        Message(id=f"m{i}", session_id="session-1", role="user" if i % 2 == 1 else "assistant", content=f"Message {i}")
        for i in range(1, 6)
    ]
    session.messages = messages
    
    summary_record = ConversationSummary(
        id="sum-1",
        session_id="session-1",
        summary="User discussed preliminary architecture details.",
        last_message_id="m3"
    )
    
    with pytest.MonkeyPatch.context() as mp:
        mock_repo = MagicMock()
        mock_repo.get_session = AsyncMock(return_value=session)
        mock_repo.get_summary = AsyncMock(return_value=summary_record)
        mp.setattr("app.modules.brain.context.SessionRepository", lambda db: mock_repo)
        
        context = await engine.build_context("session-1", "Next topic", mock_db)
        
        # System prompt should include summary
        assert "[CONVERSATION CONTEXT & SUMMARY]" in context[0]["content"]
        assert "User discussed preliminary architecture details." in context[0]["content"]
        
        # Context should only have system + last 2 recent messages + current message = 4 items
        assert len(context) == 4
        assert context[1] == {"role": "assistant", "content": "Message 4"}
        assert context[2] == {"role": "user", "content": "Message 5"}
        assert context[3] == {"role": "user", "content": "Next topic"}
