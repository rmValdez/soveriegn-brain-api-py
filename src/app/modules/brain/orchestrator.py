from typing import AsyncGenerator, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.ollama.chat import generate_chat_response, stream_chat_response
from app.modules.sessions.repository import SessionRepository
from .decisions import parse_decision_from_llm, BrainDecision
from .planner import PlannerService

class BrainOrchestrator:
    """
    The Brain Orchestrator is responsible for deciding what the user request requires.
    In Phase 6, it intercepts the incoming message and routes it.
    """
    
    def __init__(self):
        self.planner = PlannerService()
    
    async def process_message(self, message: str, db: AsyncSession, session_id: Optional[str] = None) -> Tuple[str, str]:
        repo = SessionRepository(db)
        
        if not session_id:
            session = await repo.create_session()
            session_id = session.id
            
        await repo.add_message(session_id, "user", message)
        
        # Phase 6: Initial decision parsing
        # We pass the message to a fast LLM or rule-based parser to get intent
        decision = parse_decision_from_llm(message)
        
        if decision.action != "answer":
            # Route to planner
            response = await self.planner.execute_plan(decision)
        else:
            # Fetch history and answer directly
            session = await repo.get_session(session_id)
            messages_context = [{"role": m.role, "content": m.content} for m in session.messages]
            response = await generate_chat_response(messages_context)
        
        await repo.add_message(session_id, "assistant", response)
        return response, session_id
        
    async def process_message_stream(self, message: str, db: AsyncSession, session_id: Optional[str] = None) -> AsyncGenerator[str, None]:
        repo = SessionRepository(db)
        
        if not session_id:
            session = await repo.create_session()
            session_id = session.id
            
        await repo.add_message(session_id, "user", message)
        
        decision = parse_decision_from_llm(message)
        
        if decision.action != "answer":
            # Cannot easily stream tool execution right now, yield final result
            response = await self.planner.execute_plan(decision)
            yield response
            await repo.add_message(session_id, "assistant", response)
            return
            
        session = await repo.get_session(session_id)
        messages_context = [{"role": m.role, "content": m.content} for m in session.messages]
        
        full_response = ""
        async for token in stream_chat_response(messages_context):
            full_response += token
            yield token
            
        # Save assistant message after stream finishes
        await repo.add_message(session_id, "assistant", full_response)
