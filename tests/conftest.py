"""
KnowledgeSavvy - Test Configuration and Fixtures

This module contains pytest fixtures and configuration shared across all tests.
It provides database setup, mock objects, and test data for consistent testing.
"""

from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import only the models, not the connection module
from database import models


@pytest.fixture
def temp_db():
    """
    Create a temporary in-memory SQLite database for testing.

    This fixture provides a clean database for each test without affecting
    the production database. It automatically creates tables and cleans up.

    Note: Uses SQLite for speed and isolation, even though production uses PostgreSQL.
    SQLite is the best practice for unit tests as it's fast and requires no infrastructure.
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables
    models.Base.metadata.create_all(engine)

    # Create session
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    yield session

    # Cleanup
    session.close()
    engine.dispose()


@pytest.fixture
def postgres_test_db():
    """
    Create a test database in PostgreSQL for integration tests.

    This fixture is for integration tests that need to verify PostgreSQL-specific
    behavior. Requires PostgreSQL to be running with test credentials.

    Usage: Mark tests with @pytest.mark.database to use this fixture.

    Note: Slower than SQLite, use only when PostgreSQL-specific features are needed.
    """
    from config.settings import settings

    # Create test database URL (using test database)
    test_db_url = settings.resolved_database_url.replace(
        settings.postgres_db, f"{settings.postgres_db}_test"
    )

    # Create engine
    engine = create_engine(test_db_url, echo=False)

    # Create all tables
    models.Base.metadata.create_all(engine)

    # Create session
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    yield session

    # Cleanup
    session.close()
    models.Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def mock_vector_store():
    """
    Mock vector store for testing without external dependencies.

    Returns a mock that simulates vector store operations for testing
    vector store manager functionality.
    """
    mock_vs = MagicMock()
    mock_vs.add_documents.return_value = ["doc1", "doc2"]
    mock_vs.similarity_search.return_value = [
        MagicMock(page_content="Test content 1", metadata={"source": "test1.txt"}),
        MagicMock(page_content="Test content 2", metadata={"source": "test2.txt"}),
    ]
    mock_vs.similarity_search_with_score.return_value = [
        (MagicMock(page_content="Test content", metadata={"source": "test.txt"}), 0.95)
    ]
    return mock_vs


@pytest.fixture
def sample_collection_data():
    """Provide sample collection data for testing."""
    return {"name": "test-collection", "description": "Test collection for unit tests"}


@pytest.fixture
def sample_source_data():
    """Provide sample source data for testing."""
    return {
        "title": "Test Document",
        "type": "pdf",
        "collection_name": "test-collection",
        "ids": ["chunk1", "chunk2", "chunk3"],
    }


@pytest.fixture
def mock_vs_config():
    """Provide mock vector store configuration for testing."""
    mock_config = MagicMock()
    mock_config.backend = "chroma"
    mock_config.collection_name = "test-collection"
    mock_config.persist_dir = None
    return mock_config


@pytest.fixture
def mock_embedding():
    """Provide mock embedding model for vector store testing."""
    mock_emb = MagicMock()
    mock_emb.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    mock_emb.embed_query.return_value = [0.1, 0.2, 0.3]
    return mock_emb
