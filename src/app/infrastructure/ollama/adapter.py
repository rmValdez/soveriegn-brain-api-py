from typing import AsyncGenerator, Optional, List, Dict
import ollama
from app.core.config import settings
from app.modules.brain.interfaces import LLMProvider
from app.infrastructure.ollama.client import client as default_ollama_client

class OllamaAdapter(LLMProvider):
    """
    Ollama implementation of LLMProvider.
    Ensures Ollama is the exclusive, dedicated AI runtime for Sovereign Brain.
    """
    def __init__(self, ollama_client: Optional[ollama.AsyncClient] = None):
        self.client = ollama_client or default_ollama_client

    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        target_model = model or settings.ollama_general_model
        try:
            response = await self.client.chat(
                model=target_model,
                messages=messages,
                keep_alive=settings.ollama_keep_alive,
            )
            return response["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Ollama execution error ({target_model}): {str(e)}") from e

    async def stream_chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> AsyncGenerator[str, None]:
        target_model = model or settings.ollama_general_model
        try:
            stream = await self.client.chat(
                model=target_model,
                messages=messages,
                stream=True,
                keep_alive=settings.ollama_keep_alive,
            )
            async for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    yield chunk["message"]["content"]
        except Exception as e:
            yield f"\n[Error streaming from Ollama ({target_model}): {str(e)}]"
