"""
KnowledgeSavvy - Vector Store Factory Module

This module provides a factory function for creating different types of vector stores
based on configuration. It supports multiple backends including Chroma, Pinecone,
and PostgreSQL with pgvector, providing a unified interface for vector operations.

The factory handles:
- Backend-specific configuration and initialization
- Automatic index creation for cloud-based services
- Consistent interface across different vector store implementations
- Fallback mechanisms and error handling


"""

import os

from langchain.vectorstores import VectorStore
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_postgres import PGVector
from pinecone import Pinecone, ServerlessSpec

from .config import DEFAULTS, VectorStoreConfig


def get_vectorstore(config: VectorStoreConfig, embedding: Embeddings) -> VectorStore:
    """
    Create and return a vector store instance based on the specified backend.

    This factory function creates the appropriate vector store backend based on
    the configuration. It handles backend-specific setup, index creation, and
    configuration to ensure consistent behavior across different implementations.

    Supported backends:
    - chroma: Local file-based vector store with persistence
    - pgvector: PostgreSQL-based vector store with pgvector extension
    - pinecone: Cloud-based vector store with automatic index management

    Args:
        config (VectorStoreConfig): Configuration object specifying backend and parameters
        embedding (Embeddings): Embedding model for vector creation

    Returns:
        VectorStore: Configured vector store instance

    Raises:
        ValueError: If the specified backend is not supported
    """
    backend = config.backend

    if backend == "chroma":
        # Chroma: Local file-based vector store
        return Chroma(
            collection_name=config.collection_name,
            embedding_function=embedding,
            persist_directory=config.persist_dir or DEFAULTS["chroma"]["persist_dir"],
        )

    elif backend == "pgvector":
        # PGVector: PostgreSQL with pgvector extension
        return PGVector(
            connection=config.pg_conn_str or DEFAULTS["pgvector"]["connection_string"],
            collection_name=config.collection_name,
            embeddings=embedding,
        )

    elif backend == "pinecone":
        # Pinecone: Cloud-based vector store
        pc = Pinecone()

        # Create the index if it doesn't exist
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if config.collection_name not in existing_indexes:
            pc.create_index(
                name=config.collection_name,
                dimension=1536,  # Depends on the embedding model
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )

        # Return Pinecone vector store instance
        return PineconeVectorStore(
            index_name=config.collection_name, embedding=embedding
        )

    else:
        raise ValueError(f"Unsupported backend: {backend}")
