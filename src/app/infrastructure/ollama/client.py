import ollama
from app.core.config import settings

# Create a customized AsyncClient configured with the base URL
client = ollama.AsyncClient(host=settings.ollama_base_url)
