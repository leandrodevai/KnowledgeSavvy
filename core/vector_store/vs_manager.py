"""
KnowledgeSavvy - Vector Store Manager Module

This module provides a unified interface for vector store operations across
different vendor implementations (Chroma, Pinecone, PostgreSQL+pgvector).

The main goal is to abstract vendor-specific implementations, allowing the
application to switch between backends seamlessly. When adding new vendors,
update the conditional logic in delete_collection() and delete_documents()
methods to handle the new backend's specific API.

Key abstraction benefits:
- Vendor-agnostic document operations
- Consistent error handling across backends
- Easy backend switching via configuration
"""

from typing import List

from langchain_core.embeddings import Embeddings

from .vs_factory import VectorStoreConfig, get_vectorstore


class VectorStoreManager:
    """
    Unified interface for vector store operations across different vendors.

    Abstracts vendor-specific implementations to provide consistent behavior
    regardless of the underlying vector store (Chroma, Pinecone, PostgreSQL+pgvector).

    Note: When adding new vendors, update delete_collection() and delete_documents()
    methods to handle the new backend's specific deletion API.
    """

    def __init__(self, config: VectorStoreConfig, embedding: Embeddings):
        """
        Initialize the manager with vector store configuration and embedding model.

        Args:
            config: Vector store configuration (backend, collection name, etc.)
            embedding: Embedding model to use for document vectorization
        """
        self.config = config
        self.vectorstore = get_vectorstore(config, embedding)

    def add_documents(self, docs):
        """Add documents with embeddings to the vector store."""
        return self.vectorstore.add_documents(docs)

    def similarity_search(self, query: str, k: int = 4):
        """Search for similar documents in the collection."""
        return self.vectorstore.similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: int = 4):
        """Search for similar documents including similarity scores."""
        return self.vectorstore.similarity_search_with_score(query, k=k)

    def as_retriever(self, **kwargs):
        """Return a retriever interface for the vector store."""
        return self.vectorstore.as_retriever(**kwargs)

    def delete_collection(self):
        """
        Delete the entire collection and all its documents.

        WARNING: This operation is irreversible.
        """
        # Backend-specific implementations - extend here for new vendors
        if self.config.backend == "chroma":
            self.vectorstore.delete_collection()
        elif self.config.backend == "pinecone":
            import pinecone

            pinecone.delete_index(self.config.pinecone_index)
        elif self.config.backend == "pgvector":
            # PostgreSQL: Clear all records from collection table
            with self.vectorstore._connection.connect() as conn:
                conn.execute(f"DELETE FROM {self.config.collection_name};")
        else:
            raise ValueError(f"Unsupported backend: {self.config.backend}")

    def delete_documents(self, ids: List[str]):
        """Delete specific documents' chunks by their IDs."""
        # Backend-specific implementations - extend here for new vendors
        if self.config.backend == "chroma":
            self.vectorstore.delete(ids=ids)
        elif self.config.backend == "pinecone":
            self.vectorstore._index.delete(ids=ids)
        elif self.config.backend == "pgvector":
            with self.vectorstore._connection.connect() as conn:
                conn.execute(
                    f"DELETE FROM {self.config.collection_name} WHERE id = ANY(:ids)",
                    {"ids": ids},
                )
        else:
            raise ValueError(f"Unsupported backend: {self.config.backend}")
