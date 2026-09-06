from typing import List, Dict, Optional
import re
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.brain.interfaces import LLMProvider
from app.infrastructure.ollama.adapter import OllamaAdapter
from app.modules.sessions.repository import SessionRepository
from app.modules.sessions.models import Session, Message
from app.modules.memory.repository import MemoryRepository
from app.modules.memory.schemas import MemoryCreate
from app.modules.memory.models import MemoryType

SOVEREIGN_SYSTEM_PROMPT = (
    "You are Sovereign Brain, a local-first, context-aware autonomous AI assistant.\n"
    "You prioritize precision, clarity, technical accuracy, and concise reasoning.\n"
    "When context, conversation summaries, or user memories are provided, seamlessly integrate them into your responses.\n"
    "Always maintain an objective, capable, and sovereign demeanor."
)

class ContextEngine:
    """
    Context Engine for Sovereign Brain.
    Decides what information from conversation history, summaries, long-term memory,
    and knowledge is relevant for the model given a token budget.
    """

    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        max_context_tokens: int = 4096,
        recent_messages_limit: int = 8,
        summary_trigger_threshold: int = 10,
        summary_rebuild_gap: int = 6
    ):
        self.llm = llm or OllamaAdapter()
        self.max_context_tokens = max_context_tokens
        self.recent_messages_limit = recent_messages_limit
        self.summary_trigger_threshold = summary_trigger_threshold
        self.summary_rebuild_gap = summary_rebuild_gap

    async def build_context(
        self,
        session_id: str,
        current_user_message: str,
        db: AsyncSession
    ) -> List[Dict[str, str]]:
        """
        Builds the structured context array for LLMProvider consumption:
        1. System Prompt (enhanced with relevant long-term memories and conversation summary).
        2. Sliding window of recent message turns.
        3. Current user message.
        """
        repo = SessionRepository(db)
        session = await repo.get_session(session_id)

        system_content = SOVEREIGN_SYSTEM_PROMPT

        # 1. Retrieve relevant long-term memories via Hybrid Search
        try:
            query_vector = await self.llm.get_embedding(current_user_message)
            mem_repo = MemoryRepository(db)
            memories = await mem_repo.search_hybrid(
                query=current_user_message,
                query_vector=query_vector if query_vector else None,
                limit=4
            )
            if memories:
                memory_lines = [
                    f"- [{m.type.value if hasattr(m.type, 'value') else m.type}] {m.content}"
                    for m in memories
                ]
                system_content += (
                    f"\n\n[LONG-TERM MEMORIES]\n"
                    f"The following durable context has been remembered:\n"
                    + "\n".join(memory_lines)
                )
        except Exception:
            # Memory retrieval is resilient and non-blocking
            pass

        if not session or not session.messages:
            return [
                {"role": "system", "content": system_content},
                {"role": "user", "content": current_user_message}
            ]

        total_messages = len(session.messages)

        # 2. Check if conversation exceeds threshold for rolling summarization
        if total_messages > self.summary_trigger_threshold:
            summary_record = await repo.get_summary(session_id)
            
            # Check if summary needs generation/refresh
            if not summary_record or self._should_refresh_summary(session, summary_record):
                try:
                    summary_record = await self._refresh_summary(session, repo)
                except Exception:
                    pass

            if summary_record and summary_record.summary:
                system_content += (
                    f"\n\n[CONVERSATION CONTEXT & SUMMARY]\n"
                    f"The following is a compressed summary of earlier conversation turns:\n"
                    f"{summary_record.summary}"
                )

            # Keep only the most recent N messages
            recent_messages = session.messages[-self.recent_messages_limit:]
        else:
            # Short conversation: keep all prior messages
            recent_messages = session.messages

        context: List[Dict[str, str]] = [
            {"role": "system", "content": system_content}
        ]

        # 3. Append recent turns (avoiding duplicate if already in DB)
        for msg in recent_messages:
            if msg == recent_messages[-1] and msg.role == "user" and msg.content.strip() == current_user_message.strip():
                continue
            context.append({"role": msg.role, "content": msg.content})

        # 4. Append current user message
        context.append({"role": "user", "content": current_user_message})

        return context

    async def extract_memory_if_instructed(
        self,
        session_id: str,
        user_message: str,
        db: AsyncSession
    ) -> Optional[str]:
        """
        Detects explicit memory commands (e.g. 'remember that...', 'we decided that...')
        and persists them into the long-term memories table.
        """
        patterns = [
            r"^(?:please\s+)?remember\s+(?:that\s+)?(.+)",
            r"^(?:keep\s+in\s+mind|never\s+forget)\s+(?:that\s+)?(.+)",
            r"^(?:my\s+preference\s+is\s+to|i\s+prefer)\s+(.+)",
            r"^(?:we\s+decided\s+that|decision:)\s+(.+)"
        ]

        fact = None
        mem_type = MemoryType.fact

        for p in patterns:
            match = re.search(p, user_message.strip(), re.IGNORECASE)
            if match:
                fact = match.group(1).strip()
                if "prefer" in p:
                    mem_type = MemoryType.preference
                elif "decid" in p:
                    mem_type = MemoryType.decision
                break

        if not fact:
            return None

        try:
            mem_repo = MemoryRepository(db)
            embedding = await self.llm.get_embedding(fact)
            memory_obj = MemoryCreate(
                user_id="default_user",
                type=mem_type,
                subject=fact[:40] + "..." if len(fact) > 40 else fact,
                content=fact,
                importance="high",
                confidence=1.0,
                source_session_id=session_id
            )
            await mem_repo.create(memory_obj, embedding=embedding if embedding else None)
            return fact
        except Exception:
            return None

    def _should_refresh_summary(self, session: Session, summary_record) -> bool:
        if not summary_record.last_message_id:
            return True

        message_ids = [m.id for m in session.messages]
        if summary_record.last_message_id not in message_ids:
            return True

        last_idx = message_ids.index(summary_record.last_message_id)
        unsummarized_count = len(message_ids) - 1 - last_idx
        return unsummarized_count >= self.summary_rebuild_gap

    async def _refresh_summary(self, session: Session, repo: SessionRepository):
        older_messages = session.messages[:-self.recent_messages_limit]
        if not older_messages:
            return None

        transcript = "\n".join([f"{m.role.capitalize()}: {m.content}" for m in older_messages])
        
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are the conversation compression engine for Sovereign Brain.\n"
                    "Summarize the key facts, user preferences, technical decisions, and main topics from this conversation history.\n"
                    "Be dense, factual, and concise. Do not use conversational filler or preambles."
                )
            },
            {
                "role": "user",
                "content": f"Summarize this earlier conversation history:\n\n{transcript}"
            }
        ]

        summary_text = await self.llm.chat(prompt)
        last_summarized_message = older_messages[-1]

        summary_record = await repo.upsert_summary(
            session_id=session.id,
            summary=summary_text.strip(),
            last_message_id=last_summarized_message.id
        )
        return summary_record
