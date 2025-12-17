"""
Tests for vector store manager operations.

This module tests the VectorStoreManager abstraction layer that provides
a unified interface across different vector store backends (Chroma, Pinecone, pgvector).
"""

from unittest.mock import MagicMock, call, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from core.vector_store.vs_manager import VectorStoreManager


class TestVectorStoreManager:
    """Test VectorStoreManager wrapper methods."""

    @pytest.mark.unit
    def test_add_documents(self, mock_vs_config, mock_vector_store, mock_embedding):
        """Verify add_documents passes through to underlying store."""
        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)
            docs = [MagicMock(page_content="test")]

            result = manager.add_documents(docs)

            mock_vector_store.add_documents.assert_called_once_with(docs)
            assert result == ["doc1", "doc2"]

    @pytest.mark.unit
    def test_similarity_search(self, mock_vs_config, mock_vector_store, mock_embedding):
        """Verify similarity_search passes query to underlying store."""
        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)

            result = manager.similarity_search("test query", k=5)

            mock_vector_store.similarity_search.assert_called_once_with(
                "test query", k=5
            )
            assert len(result) == 2

    @pytest.mark.unit
    def test_similarity_search_with_score(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Verify similarity_search_with_score returns scores."""
        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)

            results = manager.similarity_search_with_score("test query", k=3)

            mock_vector_store.similarity_search_with_score.assert_called_once_with(
                "test query", k=3
            )
            assert len(results) == 1
            assert results[0][1] == 0.95


class TestDeleteOperations:
    """Test backend-specific deletion methods."""

    @pytest.mark.unit
    def test_delete_collection_chroma(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Test Chroma backend uses built-in delete_collection."""
        mock_vs_config.backend = "chroma"

        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)
            manager.delete_collection()

            mock_vector_store.delete_collection.assert_called_once()

    @pytest.mark.unit
    def test_delete_collection_pinecone(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Test Pinecone backend deletes index."""
        mock_vs_config.backend = "pinecone"
        mock_vs_config.pinecone_index = "test-index"

        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            with patch("pinecone.delete_index") as mock_delete:
                manager = VectorStoreManager(mock_vs_config, mock_embedding)
                manager.delete_collection()

                mock_delete.assert_called_once_with("test-index")

    @pytest.mark.unit
    def test_delete_collection_pgvector(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Test pgvector backend clears table."""
        mock_vs_config.backend = "pgvector"
        mock_vs_config.collection_name = "test_collection"

        mock_connection = MagicMock()
        mock_conn_context = MagicMock()
        mock_connection.connect.return_value.__enter__ = MagicMock(
            return_value=mock_conn_context
        )
        mock_connection.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_vector_store._connection = mock_connection

        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)
            manager.delete_collection()

            mock_conn_context.execute.assert_called_once()

    @pytest.mark.unit
    def test_delete_collection_unsupported_backend(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Verify unsupported backend raises ValueError."""
        mock_vs_config.backend = "unsupported"

        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)

            with pytest.raises(ValueError, match="Unsupported backend"):
                manager.delete_collection()

    @pytest.mark.unit
    def test_delete_documents_chroma(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Test document deletion in Chroma."""
        mock_vs_config.backend = "chroma"
        ids = ["id1", "id2", "id3"]

        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)
            manager.delete_documents(ids)

            mock_vector_store.delete.assert_called_once_with(ids=ids)

    @pytest.mark.unit
    def test_delete_documents_pinecone(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Test document deletion in Pinecone."""
        mock_vs_config.backend = "pinecone"
        ids = ["id1", "id2"]

        mock_index = MagicMock()
        mock_vector_store._index = mock_index

        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)
            manager.delete_documents(ids)

            mock_index.delete.assert_called_once_with(ids=ids)

    @pytest.mark.unit
    def test_delete_documents_pgvector(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Test document deletion in pgvector."""
        mock_vs_config.backend = "pgvector"
        mock_vs_config.collection_name = "test_collection"
        ids = ["id1", "id2", "id3"]

        mock_connection = MagicMock()
        mock_conn_context = MagicMock()
        mock_connection.connect.return_value.__enter__ = MagicMock(
            return_value=mock_conn_context
        )
        mock_connection.connect.return_value.__exit__ = MagicMock(return_value=False)
        mock_vector_store._connection = mock_connection

        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)
            manager.delete_documents(ids)

            # Verify SQL execution was called
            mock_conn_context.execute.assert_called_once()
            call_args = mock_conn_context.execute.call_args
            # Verify the SQL statement contains the table name
            assert "DELETE FROM test_collection" in str(call_args)


@pytest.mark.integration
class TestVectorStoreIntegration:
    """Integration tests for vector store workflows."""

    def test_add_search_delete_workflow(
        self, mock_vs_config, mock_vector_store, mock_embedding
    ):
        """Test complete workflow: add documents, search, then delete."""
        with patch(
            "core.vector_store.vs_manager.get_vectorstore",
            return_value=mock_vector_store,
        ):
            manager = VectorStoreManager(mock_vs_config, mock_embedding)

            # Add documents
            docs = [MagicMock(page_content=f"content {i}") for i in range(3)]
            manager.add_documents(docs)

            # Search
            results = manager.similarity_search("test", k=2)
            assert len(results) > 0

            # Delete specific documents
            mock_vs_config.backend = "chroma"
            manager.delete_documents(["id1", "id2"])

            # Verify operations executed
            mock_vector_store.add_documents.assert_called_once()
            mock_vector_store.similarity_search.assert_called_once()
            mock_vector_store.delete.assert_called_once()
