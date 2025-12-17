"""
KnowledgeSavvy - Vector Store Configuration Module

This module defines the configuration structure for vector stores used in the
KnowledgeSavvy system. It provides a Pydantic model for vector store configuration
and default values for different backends.

The configuration supports:
- Multiple vector store backends (Chroma, Pinecone, PGVector)
- Backend-specific configuration parameters
- Environment variable integration
- Default values for common configurations


"""

import os
from typing import Literal, Optional

# from langchain.vectorstores import Chroma, Pinecone, PGVector
from pydantic import BaseModel, ConfigDict

from config import settings


class VectorStoreConfig(BaseModel):
    """
    Configuration model for vector store backends.

    This Pydantic model defines the configuration structure for different
    vector store backends, including backend type, collection name, and
    backend-specific parameters.

    Attributes:
        backend: Type of vector store backend to use
        collection_name: Name of the collection for document storage
        persist_dir: Directory for Chroma persistence (optional)
        pg_conn_str: PostgreSQL connection string for pgvector (optional)
    """

    # model_config = ConfigDict(arbitrary_types_allowed=True)
    backend: Literal["chroma", "pinecone", "pgvector"]
    collection_name: str
    # embedding_model: Embeddings

    # Chroma-specific configuration
    persist_dir: Optional[str] = None

    # PGVector-specific configuration
    pg_conn_str: Optional[str] = None


# Default configuration values for each backend
DEFAULTS = {
    "chroma": {"persist_dir": settings.chroma_persist_dir},
    "pgvector": {"connection_string": settings.resolved_database_url},
}
