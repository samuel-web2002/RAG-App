"""Application configuration using pydantic-settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "RAG Chatbot API"
    app_version: str = "1.0.0"
    debug: bool = False
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Security
    api_key: str = "dev-secret-change-me"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    model_name: str = "llama3"
    embedding_model: str = "nomic-embed-text"
    temperature: float = 0.2
    max_tokens: int = 2048

    # ChromaDB
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "rag_documents"

    # RAG tuning
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retriever_k: int = 6

    # Conversation memory
    memory_window: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
