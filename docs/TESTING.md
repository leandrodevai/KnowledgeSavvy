# KnowledgeSavvy Tests

This directory contains the test suite for KnowledgeSavvy. Tests are organized by module and use pytest for execution with comprehensive fixtures and mocking strategies.

## Test Structure

```
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_crud.py         # Database CRUD operations tests (10 tests)
├── test_vs_manager.py   # Vector store manager tests (11 tests)
├── test_config.py       # Configuration and settings tests (7 tests)
```

**Total Test Coverage**: 28 unit tests + 1 integration test

## Quick Start

### Using Pipenv (Recommended)
```bash
# Activate virtual environment
pipenv shell

# Run all unit tests (fast, SQLite in-memory)
python -m pytest tests/ -m unit -v

# Run specific test file
python -m pytest tests/test_vs_manager.py -v

# Run DB/integration tests (requires Docker PostgreSQL)
docker compose up -d postgres_kns
python -m pytest tests/ -m "database or integration" -v
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_crud.py -v
pytest tests/test_vs_manager.py -v
pytest tests/test_config.py -v
```

### Run tests by marker
```bash
# Unit tests only (fast, uses SQLite in-memory)
pytest -m unit -v

# Integration tests only (tests complete workflows)
docker compose up -d postgres_kns
pytest -m integration -v

# Database tests (requires PostgreSQL)
docker compose up -d postgres_kns
pytest -m database -v

# Exclude slow tests
pytest -m "not slow"
```

### Run with coverage
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report (macOS)
# On Windows: start htmlcov\index.html
```

## Test Markers

Tests are categorized using pytest markers for selective execution:

- `@pytest.mark.unit` - Fast unit tests using SQLite in-memory (no external dependencies)
- `@pytest.mark.integration` - Integration tests for complete workflows
- `@pytest.mark.database` - Tests requiring PostgreSQL with real connections
- `@pytest.mark.slow` - Tests that take longer to run (>1 second)

## Fixtures

All fixtures are defined in `conftest.py` and automatically available to all tests.

### Database Fixtures
- `temp_db` - **SQLite in-memory database** for unit tests
  - Fast, isolated, no setup required
  - Automatically creates/destroys tables per test
  - Use for CRUD operation tests
  
- `postgres_test_db` - **PostgreSQL test database** for integration tests
  - Requires PostgreSQL with pgvector extension
  - Start the Docker service `postgres_kns` before running
  - Use markers `integration` or `database` when executing
  - Use for testing production-like scenarios

### Mock Fixtures
- `mock_vector_store` - **Mock Chroma vectorstore**
  - Pre-configured with common return values
  - Methods: `add_documents()`, `similarity_search()`, `similarity_search_with_score()`, `delete()`
  - No external API calls required
  
- `mock_vs_config` - **Mock VectorStoreConfig**
  - Backend set to "chroma" by default
  - Collection name: "test-collection"
  - Configurable for testing different backends
  
- `mock_embedding` - **Mock embedding model**
  - Simulates `embed_documents()` and `embed_query()` methods
  - Returns dummy vectors: `[[0.1, 0.2, 0.3]]` and `[0.1, 0.2, 0.3]`
  - Required for VectorStoreManager initialization

### Data Fixtures
- `sample_collection_data` - Sample collection for testing
  ```python
  {"name": "test-collection", "description": "Test collection for unit tests"}
  ```
  
- `sample_source_data` - Sample source/document data
  ```python
  {"title": "Test Document", "type": "pdf", "collection_name": "test-collection", "ids": ["chunk1", "chunk2", "chunk3"]}
  ```

## Test Organization

### test_crud.py (10 tests)
Tests database CRUD operations with SQLite in-memory database:
- **TestCollectionOperations**: Create, retrieve, delete collections
- **TestSourceOperations**: Manage document sources within collections
- **TestDocumentIdOperations**: Handle vector store chunk identifiers

**Key Pattern**: Uses `@db_operation` decorator for session management

### test_vs_manager.py (11 tests)
Tests vector store abstraction layer with mocked backends:
- **TestVectorStoreManager**: Basic operations (add, search, retrieve)
- **TestDeleteOperations**: Backend-specific deletion (Chroma, Pinecone, pgvector)
- **TestVectorStoreIntegration**: Complete add-search-delete workflow

**Key Pattern**: Patches `get_vectorstore` to avoid real API calls

### test_config.py (7 tests)
Tests configuration, SSL setup, and logging:
- **TestSSLConfiguration**: SSL context and certificate configuration
- **TestSettingsConfiguration**: Environment variable loading via Pydantic Settings
- **TestLoggingConfiguration**: Log handler setup and module logger creation

**Key Pattern**: Uses environment variable patching for isolated tests

## Writing Tests

### Example: Unit Test with Database
```python
@pytest.mark.unit
def test_create_collection(temp_db, sample_collection_data):
    """Test collection creation with SQLite in-memory DB."""
    collection = crud.create_collection(
        sample_collection_data["name"],
        sample_collection_data["description"]
    )
    
    # Query DB directly (decorator closes session after CRUD operation)
    db_collection = temp_db.query(models.Collection).filter_by(
        name=sample_collection_data["name"]
    ).first()
    
    assert db_collection is not None
    assert db_collection.name == sample_collection_data["name"]
```

### Example: Unit Test with Mocked Vector Store
```python
from unittest.mock import patch, MagicMock

@pytest.mark.unit
def test_add_documents(mock_vs_config, mock_vector_store, mock_embedding):
    """Test document addition through VectorStoreManager."""
    with patch('core.vector_store.vs_manager.get_vectorstore', return_value=mock_vector_store):
        manager = VectorStoreManager(mock_vs_config, mock_embedding)
        docs = [MagicMock(page_content="test")]
        
        result = manager.add_documents(docs)
        
        mock_vector_store.add_documents.assert_called_once_with(docs)
        assert result == ["doc1", "doc2"]
```

### Example: Integration Test
```python
@pytest.mark.integration
def test_complete_workflow(mock_vs_config, mock_vector_store, mock_embedding):
    """Test end-to-end vector store workflow."""
    with patch('core.vector_store.vs_manager.get_vectorstore', return_value=mock_vector_store):
        manager = VectorStoreManager(mock_vs_config, mock_embedding)
        
        # Add documents
        docs = [MagicMock(page_content=f"content {i}") for i in range(3)]
        manager.add_documents(docs)
        
        # Search
        results = manager.similarity_search("test", k=2)
        assert len(results) > 0
        
        # Verify call chain
        mock_vector_store.add_documents.assert_called_once()
        mock_vector_store.similarity_search.assert_called_once()
```

## Testing Best Practices

### Mocking Strategy
- **Mock external dependencies**: Always mock API calls, vector stores, and LLMs
- **Patch at usage point**: Use `'module.where.used'` not `'module.where.defined'`
- **Return realistic values**: Mock return values should match real API responses

### Database Testing
- **Use temp_db for unit tests**: Fast, isolated, no cleanup needed
- **Query DB directly in assertions**: CRUD decorators close sessions automatically
- **Avoid DetachedInstanceError**: Don't access object attributes after session closes

### Test Isolation
- **No shared state**: Each test should be independent
- **Use fixtures**: Leverage pytest fixtures for setup/teardown
- **Mock time-sensitive operations**: Use `freezegun` for time-dependent tests

## Common Pitfalls

### 1. DetachedInstanceError with SQLAlchemy
**Problem**: Accessing model attributes after session closes
```python
# ❌ WRONG
collection = crud.create_collection("name", "desc")
assert collection.name == "name"  # DetachedInstanceError!
```

**Solution**: Query database directly
```python
# ✅ CORRECT
crud.create_collection("name", "desc")
collection = temp_db.query(models.Collection).filter_by(name="name").first()
assert collection.name == "name"
```

### 2. Incorrect Patch Path
**Problem**: Patching where function is defined instead of used
```python
# ❌ WRONG - patches factory module, not usage in vs_manager
with patch('core.vector_store.vs_factory.get_vectorstore'):
    manager = VectorStoreManager(config, embedding)
```

**Solution**: Patch where imported/used
```python
# ✅ CORRECT - patches where vs_manager imports it
with patch('core.vector_store.vs_manager.get_vectorstore', return_value=mock):
    manager = VectorStoreManager(config, embedding)
```

### 3. Missing Required Fixtures
**Problem**: VectorStoreManager requires embedding parameter
```python
# ❌ WRONG
manager = VectorStoreManager(mock_vs_config)  # TypeError!
```

**Solution**: Include mock_embedding fixture
```python
# ✅ CORRECT
def test_example(mock_vs_config, mock_embedding):
    manager = VectorStoreManager(mock_vs_config, mock_embedding)
```

## Requirements

Tests require the following packages (included in Pipfile):
- `pytest` - Test framework
- `pytest-cov` - Coverage reports
- `pytest-mock` - Enhanced mocking utilities
- `sqlalchemy` - Database ORM for tests

All dependencies are managed via Pipenv:
```bash
pipenv install --dev
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install pipenv
          pipenv install --dev
      
      - name: Run unit tests
        run: |
          pipenv run python -m pytest tests/ -m unit --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Local Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Assumes pipenv shell is active in your terminal
python -m pytest tests/ -m unit -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Debugging Tests

### Run single test with debugging
```bash
pytest tests/test_crud.py::TestCollectionOperations::test_create_collection -v -s
```

### Show print statements
```bash
pytest tests/ -v -s
```

### Stop on first failure
```bash
pytest tests/ -x
```

### Run last failed tests only
```bash
pytest --lf
```

### Show test execution times
```bash
pytest --durations=10
```
