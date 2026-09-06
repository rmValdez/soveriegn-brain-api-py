from typing import AsyncGenerator, List, Dict
from app.infrastructure.ollama.client import client
from app.core.config import settings

async def generate_chat_response(messages: List[Dict[str, str]]) -> str:
    response = await client.chat(
        model=settings.ollama_general_model,
        messages=messages,
        keep_alive=settings.ollama_keep_alive
    )
    return response["message"]["content"]

async def stream_chat_response(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    async for chunk in await client.chat(
        model=settings.ollama_general_model,
        messages=messages,
        stream=True,
        keep_alive=settings.ollama_keep_alive
    ):
        if "message" in chunk and "content" in chunk["message"]:
            yield chunk["message"]["content"]
