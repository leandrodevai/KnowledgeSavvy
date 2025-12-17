"""
Unified application settings for KnowledgeSavvy.

This module centralizes configuration across the application using
Pydantic Settings. It loads environment variables from a .env file
and provides typed access to settings.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Typed settings loaded from environment variables or .env.

    Exposes commonly used configuration across the app: database,
    vector store, logging, and API keys.
    """

    # General
    debug: bool = False

    # Vector store
    vector_store_backend: str = "chroma"  # chroma | pinecone | pgvector
    chroma_persist_dir: str = "data/vector_stores_db/chroma_store"

    # Database (PostgreSQL)
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_server: Optional[str] = None
    postgres_db: Optional[str] = None
    database_url: Optional[str] = None  # If provided, overrides composed URL

    # API Keys (optional)
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None

    # LangChain (LangSmith observability)
    langchain_tracing_v2: bool = False
    langchain_project: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def resolved_database_url(self) -> Optional[str]:
        """Return an SQLAlchemy-compatible database URL.

        Preference order:
        1) database_url if set
        2) Compose from postgres_* pieces
        """
        if self.database_url:
            return self.database_url
        if all(
            [
                self.postgres_user,
                self.postgres_password,
                self.postgres_server,
                self.postgres_db,
            ]
        ):
            return (
                f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_server}/{self.postgres_db}"
            )
        return None


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return a cached AppSettings instance."""
    return AppSettings()


# Eager, module-level instance for convenience imports
settings = get_settings()
