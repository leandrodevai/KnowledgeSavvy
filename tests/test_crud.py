"""
KnowledgeSavvy - CRUD Operations Tests

This module contains comprehensive tests for database CRUD operations.
Tests demonstrate proper database testing with fixtures, mocking, and
edge case handling for a professional portfolio.
"""

from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from database import crud, models


class TestCollectionOperations:
    """Test collection-related CRUD operations."""

    @pytest.mark.unit
    def test_get_all_collections_empty(self, temp_db):
        """Test getting collections when database is empty."""
        with patch("database.connection.Session", return_value=temp_db):
            collections = crud.get_all_collections()
            assert collections == []

    @pytest.mark.unit
    def test_create_collection_success(self, temp_db, sample_collection_data):
        """Test successful collection creation."""
        with patch("database.connection.Session", return_value=temp_db):
            collection = crud.create_collection(
                sample_collection_data["name"], sample_collection_data["description"]
            )

            # Verify collection was created by querying directly
            assert collection is not None
            result = (
                temp_db.query(models.Collection)
                .filter_by(name=sample_collection_data["name"])
                .first()
            )
            assert result is not None
            assert result.name == sample_collection_data["name"]
            assert result.description == sample_collection_data["description"]

    @pytest.mark.unit
    def test_create_collection_duplicate_name(self, temp_db, sample_collection_data):
        """Test that creating collection with duplicate name raises error."""
        with patch("database.connection.Session", return_value=temp_db):
            # Create first collection
            crud.create_collection(
                sample_collection_data["name"], sample_collection_data["description"]
            )

            # Attempt to create duplicate should raise IntegrityError
            with pytest.raises(IntegrityError):
                crud.create_collection(
                    sample_collection_data["name"], "Different description"
                )

    @pytest.mark.unit
    def test_delete_collection_exists(self, temp_db, sample_collection_data):
        """Test deleting an existing collection."""
        with patch("database.connection.Session", return_value=temp_db):
            # Create collection first
            collection = crud.create_collection(
                sample_collection_data["name"], sample_collection_data["description"]
            )

            # Delete the collection
            crud.delete_collection(sample_collection_data["name"])

            # Verify it's deleted
            collections = crud.get_all_collections()
            assert len(collections) == 0

    @pytest.mark.unit
    def test_delete_collection_not_exists(self, temp_db):
        """Test deleting a non-existent collection (should not raise error)."""
        with patch("database.connection.Session", return_value=temp_db):
            # Should not raise error
            crud.delete_collection("non-existent-collection")


class TestSourceOperations:
    """Test source-related CRUD operations."""

    @pytest.mark.unit
    def test_create_source_success(
        self, temp_db, sample_collection_data, sample_source_data
    ):
        """Test successful source creation with document IDs."""
        with patch("database.connection.Session", return_value=temp_db):
            # Create collection first
            crud.create_collection(
                sample_collection_data["name"], sample_collection_data["description"]
            )

            # Create source
            source = crud.create_source_and_add_to_collection(
                sample_source_data["title"],
                sample_source_data["type"],
                sample_source_data["collection_name"],
                sample_source_data["ids"],
            )

            assert source is not None

            # Verify by querying database directly
            result = (
                temp_db.query(models.Source)
                .filter_by(title=sample_source_data["title"])
                .first()
            )
            assert result is not None
            assert result.title == sample_source_data["title"]
            assert result.type == sample_source_data["type"]

            # Check that document IDs were created
            doc_ids = (
                temp_db.query(models.DocumentsIds).filter_by(source_id=result.id).all()
            )
            assert len(doc_ids) == len(sample_source_data["ids"])

    @pytest.mark.unit
    def test_create_source_collection_not_exists(self, temp_db, sample_source_data):
        """Test creating source for non-existent collection."""
        with patch("database.connection.Session", return_value=temp_db):
            source = crud.create_source_and_add_to_collection(
                sample_source_data["title"],
                sample_source_data["type"],
                "non-existent-collection",
                sample_source_data["ids"],
            )

            assert source is None

    @pytest.mark.unit
    def test_get_sources_in_collection(
        self, temp_db, sample_collection_data, sample_source_data
    ):
        """Test getting all sources in a collection."""
        with patch("database.connection.Session", return_value=temp_db):
            # Create collection and source
            crud.create_collection(
                sample_collection_data["name"], sample_collection_data["description"]
            )

            crud.create_source_and_add_to_collection(
                sample_source_data["title"],
                sample_source_data["type"],
                sample_source_data["collection_name"],
                sample_source_data["ids"],
            )

            # Get sources
            sources = crud.get_all_source_in_collection(sample_collection_data["name"])
            assert len(sources) == 1
            assert sources[0].title == sample_source_data["title"]

    @pytest.mark.unit
    def test_delete_source(self, temp_db, sample_collection_data, sample_source_data):
        """Test deleting a source and its document IDs."""
        with patch("database.connection.Session", return_value=temp_db):
            # Create collection and source
            crud.create_collection(
                sample_collection_data["name"], sample_collection_data["description"]
            )

            crud.create_source_and_add_to_collection(
                sample_source_data["title"],
                sample_source_data["type"],
                sample_source_data["collection_name"],
                sample_source_data["ids"],
            )

            # Get source ID from database
            source = (
                temp_db.query(models.Source)
                .filter_by(title=sample_source_data["title"])
                .first()
            )
            assert source is not None
            source_id = source.id

            # Delete source
            crud.delete_source(source_id)

            # Verify deletion
            sources = crud.get_all_source_in_collection(sample_collection_data["name"])
            assert len(sources) == 0


class TestDocumentIdOperations:
    """Test document ID-related operations."""

    @pytest.mark.unit
    def test_get_document_ids_empty_source(self, temp_db):
        """Test getting document IDs from non-existent source."""
        with patch("database.connection.Session", return_value=temp_db):
            doc_ids = crud.get_all_ids_in_source(999)  # Non-existent source ID
            assert doc_ids == []


@pytest.mark.integration
class TestCRUDWorkflow:
    """Integration tests for complete CRUD workflows."""

    def test_complete_workflow(
        self, temp_db, sample_collection_data, sample_source_data
    ):
        """Test complete workflow: create collection -> add source -> query -> delete."""
        with patch("database.connection.Session", return_value=temp_db):
            # 1. Create collection
            collection = crud.create_collection(
                sample_collection_data["name"], sample_collection_data["description"]
            )
            assert collection is not None

            # 2. Add source with documents
            source = crud.create_source_and_add_to_collection(
                sample_source_data["title"],
                sample_source_data["type"],
                sample_source_data["collection_name"],
                sample_source_data["ids"],
            )
            assert source is not None

            # 3. Query data
            collections = crud.get_all_collections()
            assert len(collections) == 1

            sources = crud.get_all_source_in_collection(sample_collection_data["name"])
            assert len(sources) == 1

            doc_ids = crud.get_all_ids_in_source(source.id)
            assert len(doc_ids) == len(sample_source_data["ids"])

            # 4. Clean up
            crud.delete_collection(sample_collection_data["name"])

            # 5. Verify cleanup
            collections = crud.get_all_collections()
            assert len(collections) == 0
