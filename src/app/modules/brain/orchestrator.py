from typing import AsyncGenerator, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.brain.interfaces import LLMProvider
from app.infrastructure.ollama.adapter import OllamaAdapter
from app.modules.sessions.repository import SessionRepository
from .decisions import parse_decision_from_llm
from .planner import PlannerService

class BrainOrchestrator:
    """
    Sovereign Brain Cognitive Orchestrator.
    Routes user requests, orchestrates planning/tools/memory,
    and executes model inference through the exclusive LLMProvider (OllamaAdapter).
    """
    
    def __init__(self, llm: Optional[LLMProvider] = None):
        self.planner = PlannerService()
        self.llm = llm or OllamaAdapter()
    
    async def process_message(
        self,
        message: str,
        db: AsyncSession,
        session_id: Optional[str] = None
    ) -> Tuple[str, str]:
        repo = SessionRepository(db)
        
        if not session_id:
            session = await repo.create_session()
            session_id = session.id
            
        await repo.add_message(session_id, "user", message)
        
        # Decision parsing for action routing
        decision = parse_decision_from_llm(message)
        
        if decision.action != "answer":
            # Route to planner execution
            response = await self.planner.execute_plan(decision)
        else:
            # Fetch conversation history and generate direct LLM response
            session = await repo.get_session(session_id)
            messages_context = [{"role": m.role, "content": m.content} for m in session.messages]
            response = await self.llm.chat(messages_context)
        
        await repo.add_message(session_id, "assistant", response)
        return response, session_id
        
    async def process_message_stream(
        self,
        message: str,
        db: AsyncSession,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        repo = SessionRepository(db)
        
        if not session_id:
            session = await repo.create_session()
            session_id = session.id
            
        await repo.add_message(session_id, "user", message)
        
        decision = parse_decision_from_llm(message)
        
        if decision.action != "answer":
            response = await self.planner.execute_plan(decision)
            yield response
            await repo.add_message(session_id, "assistant", response)
            return
            
        session = await repo.get_session(session_id)
        messages_context = [{"role": m.role, "content": m.content} for m in session.messages]
        
        full_response = ""
        async for token in self.llm.stream_chat(messages_context):
            full_response += token
            yield token
            
        # Save assistant message in PostgreSQL after stream completes
        await repo.add_message(session_id, "assistant", full_response)
