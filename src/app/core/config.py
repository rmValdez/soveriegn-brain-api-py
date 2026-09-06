from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Sovereign Brain"
    app_env: str = "development"
    
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/sovereign_brain"
    
    ollama_base_url: str = "http://localhost:11434"
    ollama_general_model: str = "qwen2.5"
    ollama_coding_model: str = "qwen2.5-coder"
    ollama_embedding_model: str = "nomic-embed-text"
    ollama_keep_alive: str = "5m"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
