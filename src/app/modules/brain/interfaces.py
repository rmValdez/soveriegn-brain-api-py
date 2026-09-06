from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, List, Dict

class LLMProvider(ABC):
    """
    Abstract interface for LLM execution in Sovereign Brain.
    Ollama is the exclusive provider implementation.
    """
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Send chat messages and return complete response text."""
        pass
        
    @abstractmethod
    async def stream_chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream chat tokens progressively."""
        pass

    @abstractmethod
    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generate vector embedding for semantic search."""
        pass
