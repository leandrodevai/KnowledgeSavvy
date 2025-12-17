# KnowledgeSavvy Developer Guide

## Overview

KnowledgeSavvy is a **Streamlit web application** that provides document management and RAG (Retrieval-Augmented Generation) capabilities through well-structured Python modules.

**Important**: This guide documents the **internal Python modules and their interfaces** for developers who want to understand or extend KnowledgeSavvy. The application is accessed through a Streamlit web interface. There are no HTTP REST endpoints.

## Table of Contents

1. [Module Architecture](#module-architecture)
2. [Database Module](#database-module) - CRUD operations with decorator pattern
3. [Document Processing](#document-processing) - Loading and indexing documents
4. [Vector Store Module](#vector-store-module) - Unified interface for multiple backends
5. [AI Models](#ai-models) - Factory pattern for embeddings and LLMs
6. [RAG Pipeline](#rag-pipeline) - LangGraph workflow
7. [Configuration](#configuration) - Environment-based settings
8. [Logging](#logging) - Centralized logging
9. [Common Usage Patterns](#common-usage-patterns) - Real-world examples
10. [Error Handling](#error-handling) - Best practices
11. [Testing](#testing) - Test fixtures and patterns
12. [Performance Considerations](#performance-considerations)
13. [Security Notes](#security-notes)

---

## Module Architecture

### Access Layers

1. **Web Interface**: Streamlit-based user interface (primary interaction method)
2. **Python Modules**: Module-level functions and classes documented below
3. **Database Layer**: SQLAlchemy ORM models
4. **Vector Store Layer**: Unified abstraction over multiple backends

### Module Organization

```
KnowledgeSavvy/
├── database/          # Database CRUD operations
├── core/             # Business logic and document processing
│   ├── ingestion.py  # Document loading and indexing
│   ├── logger.py     # Logging configuration
│   └── vector_store/ # Vector store abstraction
├── ai_agent/         # RAG pipeline (LangGraph)
├── ai_models/        # AI model factories
└── app/              # Streamlit UI modules
```

---

## Database Module

### Module: `database/crud.py`

All database operations use a decorator pattern for session management:

```python
from database import crud

# @db_operation decorator automatically handles:
# - Session creation
# - Commit on success
# - Rollback on error
# - Session cleanup
```

### Collection Operations

#### `create_collection(name: str, description: str = "") -> int`

Create a new collection for organizing documents.

**Parameters**:
- `name` (str): Collection identifier (lowercase, hyphens allowed)
- `description` (str): Optional description

**Returns**: Collection ID (int)

**Example**:
```python
collection_id = crud.create_collection(
    name="machine-learning",
    description="ML research papers"
)
```

**Validation**:
- Name must match pattern: `^[a-z0-9-]+$`
- Name must be unique

#### `get_all_collections() -> List[Dict]`

Retrieve all collections with metadata.

**Returns**: List of dictionaries with collection data

**Example**:
```python
collections = crud.get_all_collections()
# [
#   {
#     "id": 1,
#     "name": "machine-learning",
#     "description": "ML papers",
#     "created_at": datetime(...),
#     "source_count": 5
#   }
# ]
```

#### `delete_collection(collection_id: int) -> bool`

Delete a collection and all associated sources and document IDs.

**Parameters**:
- `collection_id` (int): ID of collection to delete

**Returns**: `True` on success

**Side Effects**: Cascading delete of all sources and document_ids

**Example**:
```python
success = crud.delete_collection(collection_id=1)
```

### Source Operations

#### `create_source_and_add_to_collection(...)`

Create a source record and link it to a collection.

**Parameters**:
- `title` (str): Source title (filename or URL)
- `type` (str): Source type ("pdf", "txt", "url", etc.)
- `collection_id` (int): Parent collection ID
- `doc_ids` (List[str]): List of vector store document IDs

**Returns**: Source ID (int)

**Example**:
```python
source_id = crud.create_source_and_add_to_collection(
    title="research_paper.pdf",
    type="pdf",
    collection_id=1,
    doc_ids=["doc_001", "doc_002", "doc_003"]
)
```

**Database Operations**:
1. Creates `Source` record
2. Links to `Collection`
3. Creates `DocumentsIds` records for each doc_id

#### `get_sources_by_collection(collection_id: int) -> List[Dict]`

Get all sources in a collection.

**Parameters**:
- `collection_id` (int): Collection ID

**Returns**: List of source dictionaries

**Example**:
```python
sources = crud.get_sources_by_collection(collection_id=1)
# [
#   {
#     "id": 1,
#     "title": "paper.pdf",
#     "type": "pdf",
#     "created_at": datetime(...),
#     "document_count": 10
#   }
# ]
```

#### `delete_source(source_id: int) -> Tuple[bool, List[str]]`

Delete a source and return its document IDs for vector store cleanup.

**Parameters**:
- `source_id` (int): Source ID to delete

**Returns**: Tuple of (success: bool, doc_ids: List[str])

**Example**:
```python
success, doc_ids = crud.delete_source(source_id=1)
# success = True
# doc_ids = ["doc_001", "doc_002", "doc_003"]
# Use doc_ids to delete from vector store
```

### Document ID Operations

#### `get_document_ids_by_source(source_id: int) -> List[str]`

Get all vector store document IDs for a source.

**Parameters**:
- `source_id` (int): Source ID

**Returns**: List of document ID strings

**Example**:
```python
doc_ids = crud.get_document_ids_by_source(source_id=1)
# ["doc_001", "doc_002", "doc_003"]
```

---

## Document Processing

### Module: `core/ingestion.py`

#### Class: `DocumentProcessor`

Handles document loading from various formats.

**Supported Formats**:
- PDF (`.pdf`)
- Text (`.txt`)
- Markdown (`.md`)
- Word (`.docx`)
- CSV (`.csv`)

**Methods**:

##### `load_document(file: UploadedFile) -> List[Document]`

Load and parse a document from Streamlit UploadedFile.

**Parameters**:
- `file` (UploadedFile): Streamlit file upload object

**Returns**: List of LangChain Document objects

**Example**:
```python
from core.ingestion import DocumentProcessor

processor = DocumentProcessor()
documents = processor.load_document(uploaded_file)
# Returns: [Document(page_content="...", metadata={...})]
```

**Processing Chain**:
1. Detect file type from extension
2. Route to appropriate loader (PyPDF, UnstructuredFileLoader, etc.)
3. Extract text content
4. Return as Document objects with metadata

#### Function: `index_documents(...)`

Process and index documents into vector store.

**Parameters**:
- `documents` (List[Document]): Documents to index
- `collection_name` (str): Target collection
- `source_title` (str): Source identifier
- `source_type` (str): Source type
- `chunk_size` (int): Text chunk size (default: 4000)
- `chunk_overlap` (int): Overlap between chunks (default: 200)
- `progress_callback` (Optional[Callable]): Progress update function

**Returns**: Number of chunks created (int)

**Example**:
```python
from core.ingestion import index_documents

num_chunks = index_documents(
    documents=loaded_docs,
    collection_name="research",
    source_title="paper.pdf",
    source_type="pdf",
    chunk_size=4000,
    chunk_overlap=200,
    progress_callback=lambda msg: print(msg)
)
# Returns: 25 (number of chunks created)
```

**Processing Pipeline**:
1. Split documents into chunks (RecursiveCharacterTextSplitter)
2. Calculate batch sizes based on token count
3. Generate embeddings (via EmbeddingModelFactory)
4. Store in vector store (via VectorStoreManager)
5. Save metadata to database (via CRUD operations)

#### Function: `process_url(...)`

Scrape and index web content.

**Parameters**:
- `url` (str): Website URL to scrape
- `collection_name` (str): Target collection
- `max_depth` (int): Crawl depth (1-5)
- `chunk_size` (int): Text chunk size
- `chunk_overlap` (int): Overlap between chunks
- `progress_callback` (Optional[Callable]): Progress updates

**Returns**: Number of chunks created (int)

**Example**:
```python
from core.ingestion import process_url

num_chunks = process_url(
    url="https://example.com/docs",
    collection_name="web-docs",
    max_depth=2,
    chunk_size=4000,
    chunk_overlap=200
)
```

**Requirements**: Tavily API key (`TAVILY_API_KEY` in `.env`)

---

## Vector Store Module

### Module: `core/vector_store/vs_manager.py`

#### Class: `VectorStoreManager`

Unified interface for multiple vector store backends.

**Constructor**:
```python
from core.vector_store import VectorStoreManager, VectorStoreConfig
from ai_models import EmbeddingModelFactory

config = VectorStoreConfig(
    backend="chroma",  # or "pinecone", "pgvector"
    collection_name="my-collection"
)
embedding = EmbeddingModelFactory.create_model()
manager = VectorStoreManager(config, embedding)
```

**Methods**:

##### `add_documents(documents: List[Document]) -> List[str]`

Add documents to vector store.

**Parameters**:
- `documents` (List[Document]): Documents with embeddings

**Returns**: List of document IDs

**Example**:
```python
doc_ids = manager.add_documents(chunked_documents)
# ["doc_abc123", "doc_def456", ...]
```

##### `similarity_search(query: str, k: int = 4) -> List[Document]`

Search for similar documents.

**Parameters**:
- `query` (str): Search query
- `k` (int): Number of results

**Returns**: List of most similar Documents

**Example**:
```python
results = manager.similarity_search(
    query="What is machine learning?",
    k=4
)
# Returns top 4 similar documents
```

##### `similarity_search_with_score(query: str, k: int = 4) -> List[Tuple[Document, float]]`

Search with similarity scores.

**Parameters**:
- `query` (str): Search query
- `k` (int): Number of results

**Returns**: List of (Document, score) tuples

**Example**:
```python
results = manager.similarity_search_with_score(
    query="deep learning",
    k=4
)
# [(Document(...), 0.95), (Document(...), 0.87), ...]
```

##### `as_retriever(search_kwargs: Dict = None) -> VectorStoreRetriever`

Get LangChain retriever interface.

**Parameters**:
- `search_kwargs` (Dict): Search parameters (e.g., `{"k": 4}`)

**Returns**: VectorStoreRetriever object

**Example**:
```python
retriever = manager.as_retriever(search_kwargs={"k": 4})
# Use with LangChain chains
```

##### `delete_collection() -> bool`

Delete entire collection from vector store.

**Returns**: Success boolean

**Backend-Specific Behavior**:
- **Chroma**: Deletes collection from local storage
- **Pinecone**: Deletes all vectors in namespace
- **pgvector**: Drops collection table

**Example**:
```python
success = manager.delete_collection()
```

##### `delete_documents(ids: List[str]) -> bool`

Delete specific documents by ID.

**Parameters**:
- `ids` (List[str]): Document IDs to delete

**Returns**: Success boolean

**Example**:
```python
success = manager.delete_documents(["doc_001", "doc_002"])
```

### Module: `core/vector_store/vs_factory.py`

#### Function: `get_vectorstore(config: VectorStoreConfig, embedding: Embeddings) -> VectorStore`

Factory function to create vector store instances.

**Parameters**:
- `config` (VectorStoreConfig): Configuration object
- `embedding` (Embeddings): Embedding model

**Returns**: VectorStore instance (Chroma, Pinecone, or PGVector)

**Example**:
```python
from core.vector_store import get_vectorstore, VectorStoreConfig
from ai_models import EmbeddingModelFactory

config = VectorStoreConfig(backend="chroma", collection_name="test")
embedding = EmbeddingModelFactory.create_model()
vectorstore = get_vectorstore(config, embedding)
```

---

## AI Models

### Module: `ai_models/mdl_factory.py`

#### Class: `EmbeddingModelFactory`

Factory for creating embedding models.

**Methods**:

##### `create_model() -> Embeddings`

Create embedding model from configuration.

**Returns**: Cohere embeddings model (1024 dimensions)

**Example**:
```python
from ai_models import EmbeddingModelFactory

embedding_model = EmbeddingModelFactory.create_model()
# Uses: Cohere embed-multilingual-v4.0
```

**Configuration**: Uses `COHERE_API_KEY` from environment

#### Class: `LlmModelFactory`

Factory for creating LLM models.

**Methods**:

##### `create_model(model_type: ModelType) -> BaseChatModel`

Create LLM for specific purpose.

**Parameters**:
- `model_type` (ModelType): Enum value
  - `ModelType.GENERATOR`: Answer generation
  - `ModelType.DOCUMENT_GRADING`: Document relevance
  - `ModelType.ANSWER_GROUNDING`: Hallucination detection

**Returns**: Configured LLM instance

**Example**:
```python
from ai_models import LlmModelFactory, ModelType

generator = LlmModelFactory.create_model(ModelType.GENERATOR)
# Uses: Cohere command-r-08-2024

grader = LlmModelFactory.create_model(ModelType.DOCUMENT_GRADING)
# Uses: Google Gemini 2.0 Flash
```

### Module: `ai_models/config.py`

Model configuration settings.

**Example**:
```python
from ai_models.config import models, ModelType

embedding_config = models[ModelType.EMBEDDING]
# ModelInfo(provider=COHERE, model_name="embed-multilingual-v4.0", ...)

generator_config = models[ModelType.GENERATOR]
# ModelInfo(provider=COHERE, model_name="command-r-08-2024", ...)
```

---

## RAG Pipeline

### Module: `ai_agent/graph.py`

#### Function: `create_graph() -> CompiledGraph`

Create the RAG workflow graph.

**Returns**: Compiled LangGraph workflow

**Workflow Nodes**:
1. **retrieve**: Get relevant documents from vector store
2. **grade_documents**: Score document relevance (0-10 scale)
3. **generate**: Create answer from context
4. **validate**: Two-stage validation (hallucination + quality)
5. **web_search**: Fallback to web search if needed

**Example**:
```python
from ai_agent.graph import create_graph

workflow = create_graph()

# Execute workflow
result = workflow.invoke({
    "question": "What is machine learning?",
    "collection_name": "ml-papers",
    "chat_history": []
})

# result contains:
# - answer: Generated response
# - sources: Source documents
# - web_search_used: Boolean
```

**Decision Logic**:
- If documents score ≥ 8/10: Use for generation
- If documents score < 8/10: Try web search
- Validate answer is grounded in sources
- Verify answer addresses the question

### Module: `ai_agent/chains/`

Individual LLM chain implementations:

- **`generation.py`**: Answer generation with chat history
- **`retrieval_grader.py`**: Document relevance scoring
- **`hallucination_grader.py`**: Verify answer grounding
- **`answer_grader.py`**: Verify answer quality

---

## Configuration

### Module: `config/settings.py`

#### Class: `AppSettings`

Pydantic settings with environment variable support.

**Usage**:
```python
from config.settings import settings

# Database connection
db_url = settings.resolved_database_url

# Vector store
backend = settings.vector_store_backend  # "chroma", "pinecone", "pgvector"

# API keys
google_key = settings.google_api_key
cohere_key = settings.cohere_api_key
tavily_key = settings.tavily_api_key
```

**Environment Variables**:
- `POSTGRES_*`: Database credentials
- `GOOGLE_API_KEY`: Gemini API key
- `COHERE_API_KEY`: Cohere API key
- `TAVILY_API_KEY`: Web search API key
- `VECTOR_STORE_BACKEND`: Backend choice
- `PINECONE_*`: Pinecone configuration (if used)

### Module: `config/ssl_config.py`

#### Function: `configure_ssl()`

Configure SSL certificates for HTTPS requests.

**Usage**:
```python
from config.ssl_config import configure_ssl

configure_ssl()
# Sets SSL_CERT_FILE and REQUESTS_CA_BUNDLE environment variables
```

**Called automatically** on module import.

---

## Logging

### Module: `core/logger.py`

#### Function: `setup_logging()`

Configure application logging.

**Features**:
- Rotating file handler (10MB, 5 backups)
- Console handler with colors (development)
- JSON format for file logs
- Dynamic log level (DEBUG if `DEBUG=true`)

**Usage**:
```python
import logging
from core.logger import setup_logging

setup_logging()  # Called automatically on import
logger = logging.getLogger(__name__)

logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

**Log Location**: `data/logs/KnowledgeSavvy.log`

---

## Streamlit UI Modules

### Module: `app/main.py`

Application entry point with navigation.

**Usage**:
```bash
streamlit run app/main.py
```

### Module: `app/modules/`

UI modules (not part of programmatic API):

- **`chat.py`**: Question-answering interface
- **`upload.py`**: Document/URL upload forms
- **`dashboard.py`**: Statistics and metrics
- **`management.py`**: Collection/source management

---

## Common Usage Patterns

### Complete Document Upload Flow

```python
from core.ingestion import DocumentProcessor, index_documents
from database import crud

# 1. Create collection
collection_id = crud.create_collection("research", "Research papers")

# 2. Load document
processor = DocumentProcessor()
documents = processor.load_document(uploaded_file)

# 3. Index documents
num_chunks = index_documents(
    documents=documents,
    collection_name="research",
    source_title="paper.pdf",
    source_type="pdf",
    chunk_size=4000,
    chunk_overlap=200
)

print(f"Created {num_chunks} chunks")
```

### Query Processing Flow

```python
from ai_agent.graph import create_graph

# Create workflow
workflow = create_graph()

# Execute query
result = workflow.invoke({
    "question": "Explain neural networks",
    "collection_name": "research",
    "chat_history": []
})

# Access results
answer = result["answer"]
sources = result["sources"]
used_web = result.get("web_search_used", False)
```

### Delete Collection with Cleanup

```python
from database import crud
from core.vector_store import VectorStoreManager, VectorStoreConfig
from ai_models import EmbeddingModelFactory

# 1. Get all sources
sources = crud.get_sources_by_collection(collection_id)

# 2. Delete from vector store
config = VectorStoreConfig(backend="chroma", collection_name="research")
embedding = EmbeddingModelFactory.create_model()
manager = VectorStoreManager(config, embedding)
manager.delete_collection()

# 3. Delete from database (cascades to sources and doc_ids)
crud.delete_collection(collection_id)
```

---

## Error Handling

### Database Operations

All CRUD operations use `@db_operation` decorator which:
- Automatically commits on success
- Rolls back on error
- Closes session after operation
- Logs errors

**Example**:
```python
try:
    collection_id = crud.create_collection("test", "Test")
except Exception as e:
    logger.error(f"Failed to create collection: {e}")
    # Session already rolled back and closed
```

### Vector Store Operations

```python
try:
    manager.add_documents(documents)
except Exception as e:
    logger.error(f"Vector store error: {e}")
    # Handle vector store specific errors
```

### API Key Errors

```python
from ai_models import EmbeddingModelFactory

try:
    embedding = EmbeddingModelFactory.create_model()
except ValueError as e:
    # API key not configured
    logger.error(f"Configuration error: {e}")
```

---

## Testing

### Unit Tests

Located in `tests/` directory:

- `test_crud.py`: Database operations (10 tests)
- `test_vs_manager.py`: Vector store manager (11 tests)
- `test_config.py`: Configuration (7 tests)

**Run tests**:
```bash
pipenv shell
python -m pytest tests/ -m unit -v
```

### Test Fixtures

Available in `tests/conftest.py`:

- `temp_db`: In-memory SQLite database
- `mock_vector_store`: Mocked vector store
- `mock_embedding`: Mocked embedding model
- `mock_vs_config`: Mocked configuration

**Example**:
```python
def test_create_collection(temp_db):
    collection_id = crud.create_collection("test", "Test collection")
    assert collection_id > 0
```

---

## Extending the System

### Adding a New Vector Store Backend

The system uses a factory pattern to support multiple vector stores. Here's how to add a new backend:

**1. Update VectorStoreConfig** in `core/vector_store/config.py`:

```python
class VectorStoreBackend(Enum):
    CHROMA = "chroma"
    PINECONE = "pinecone"
    PGVECTOR = "pgvector"
    MILVUS = "milvus"  # New backend
```

**2. Add factory logic** in `core/vector_store/vs_factory.py`:

```python
def get_vectorstore(config: VectorStoreConfig, embedding: Embeddings) -> VectorStore:
    if config.backend == VectorStoreBackend.CHROMA.value:
        return Chroma(...)
    elif config.backend == VectorStoreBackend.PINECONE.value:
        return Pinecone(...)
    elif config.backend == VectorStoreBackend.PGVECTOR.value:
        return PGVector(...)
    elif config.backend == VectorStoreBackend.MILVUS.value:
        # Add Milvus initialization
        from langchain_milvus import Milvus
        return Milvus(
            embedding_function=embedding,
            collection_name=config.collection_name,
            connection_args={"host": "localhost", "port": "19530"}
        )
    else:
        raise ValueError(f"Unsupported backend: {config.backend}")
```

**3. Handle backend-specific deletion** in `core/vector_store/vs_manager.py`:

```python
def delete_collection(self) -> bool:
    if self.config.backend == "chroma":
        self.vectorstore.delete_collection()
    elif self.config.backend == "pinecone":
        # Pinecone-specific logic
        ...
    elif self.config.backend == "milvus":
        # Milvus-specific logic
        self.vectorstore.col.drop()
    return True
```

**4. Update .env with new backend**:

```ini
VECTOR_STORE_BACKEND=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

### Adding a New LLM Provider

To add a new LLM provider (e.g., Anthropic Claude):

**1. Update ModelProvider** in `ai_models/base.py`:

```python
class ModelProvider(Enum):
    COHERE = "cohere"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"  # New provider
```

**2. Update model configuration** in `ai_models/config.py`:

```python
models = {
    ModelType.GENERATOR: ModelInfo(
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-sonnet-20240229",
        temperature=0.7
    ),
    # ... other models
}
```

**3. Add factory logic** in `ai_models/mdl_factory.py`:

```python
def create_model(self, model_type: ModelType) -> BaseChatModel:
    model_info = models[model_type]
    
    if model_info.provider == ModelProvider.COHERE:
        return ChatCohere(...)
    elif model_info.provider == ModelProvider.GOOGLE:
        return ChatGoogleGenerativeAI(...)
    elif model_info.provider == ModelProvider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_info.model_name,
            temperature=model_info.temperature,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
```

**4. Add API key to .env**:

```ini
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Adding a New Document Loader

To support a new document format:

**1. Update DocumentProcessor** in `core/ingestion.py`:

```python
class DocumentProcessor:
    def load_document(self, uploaded_file: UploadedFile) -> List[Document]:
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if ext == '.xlsx':  # New format
            # Excel file handling
            import pandas as pd
            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file)
            content = df.to_string()
            return [Document(
                page_content=content,
                metadata={"source": uploaded_file.name, "file_type": "xlsx"}
            )]
        # ... existing formats
```

**2. Update file uploader** in `app/modules/upload.py`:

```python
uploaded_files = st.file_uploader(
    "Select files:",
    type=['pdf', 'txt', 'docx', 'md', 'csv', 'xlsx'],  # Add new type
    accept_multiple_files=True
)
```

---

## Performance Considerations

### Document Processing

- **Chunk Size**: Larger chunks (4000-8000) for better context, smaller (1000-2000) for precision
- **Batch Processing**: Automatic batching based on token count
- **Embedding Generation**: ~0.5s per batch (Cohere API)

### Query Performance

- **Vector Search**: <100ms (Chroma local), <200ms (Pinecone)
- **Document Grading**: ~1s for 4 documents
- **Answer Generation**: ~2-4s depending on context length
- **Total Pipeline**: ~4-7s per query

### Database Performance

- **Connection Management**: Direct connections (optimized for single-user application)
- **Indexing**: Automatic on primary keys and foreign keys
- **Query Optimization**: Simple, efficient queries with SQLAlchemy ORM

---

## Security Notes

### API Keys

- Stored in `.env` file (never commit to git)
- Accessed via Pydantic Settings
- Never logged or exposed in error messages

### Database

- Password authentication required
- No raw SQL (SQLAlchemy ORM only)
- Parameterized queries prevent SQL injection

### Input Validation

- Collection names: Regex validation `^[a-z0-9-]+$`
- File types: Whitelist of allowed extensions
- No code execution in user inputs

---

## Module Design Highlights

This guide showcases:

✅ **Clean Module Design** - Well-organized Python modules with clear responsibilities  
✅ **Factory Patterns** - Flexible model creation and configuration  
✅ **Decorator Pattern** - Automatic database session management  
✅ **Strategy Pattern** - Unified interface for multiple vector store backends  
✅ **Type Safety** - Comprehensive type hints throughout  
✅ **Error Handling** - Robust error handling with detailed logging  
✅ **Testing Support** - Fixtures and patterns for comprehensive testing  

**Access Methods**:
- **Streamlit UI**: Primary user interaction method
- **Direct Python imports**: For programmatic access and testing
- **Module Interfaces**: Well-documented internal functions and classes

**Design Focus**: This project demonstrates clean Python architecture and RAG implementation. All functionality is accessible through Python module imports, making it ideal for understanding and extending the codebase.

---

## Additional Resources

- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md) for setup instructions
- **User Guide**: See [USER_GUIDE.md](USER_GUIDE.md) for end-user documentation
- **Testing**: See [TESTING.md](TESTING.md) for testing documentation
- **Documentation Index**: See [README.md](README.md) for complete documentation overview

---

## Summary

This developer guide covers:

✅ **Database Module**: CRUD operations for collections, sources, and document IDs  
✅ **Document Processing**: Loading and indexing documents  
✅ **Vector Store**: Unified interface for Chroma/Pinecone/pgvector  
✅ **AI Models**: Factories for embeddings and LLMs  
✅ **RAG Pipeline**: LangGraph workflow for question answering  
✅ **Configuration**: Settings and environment management  
✅ **Logging**: Centralized logging setup  

All functionality is accessible through **Python module imports**. Access via Streamlit UI or direct imports for testing and extension.
