# KnowledgeSavvy Architecture# KnowledgeSavvy Architecture Documentation



## System Overview## Overview



KnowledgeSavvy is a **Retrieval-Augmented Generation (RAG) system** built with Streamlit, LangChain, and LangGraph. It provides intelligent document processing and question-answering with multi-stage validation.KnowledgeSavvy is a sophisticated Retrieval-Augmented Generation (RAG) system that implements a multi-stage validation pipeline to ensure high-quality, accurate responses. The system is built using modern Python technologies and follows a modular, scalable architecture.



**Key Components**:## System Architecture

- **Web Interface**: Streamlit UI for user interaction

- **RAG Pipeline**: LangGraph workflow with validation stages### High-Level Architecture

- **Document Processing**: Multi-format ingestion and vectorization

- **Vector Storage**: Flexible backend support (Chroma, Pinecone, pgvector)```

- **Database**: PostgreSQL for metadata management┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐

│   Web Interface │    │   RAG Pipeline  │    │  Vector Store   │

---│   (Streamlit)   │◄──►│   (LangGraph)   │◄──►│   (Chroma/PG)   │

└─────────────────┘    └─────────────────┘    └─────────────────┘

## High-Level Architecture         │                       │                       │

         ▼                       ▼                       ▼

```┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐

┌──────────────────────┐│   Document      │    │   AI Models     │    │   Database      │

│   Streamlit UI       │  ← User Interface (app/)│   Processing    │    │   (Gemini/Co)   │    │   (PostgreSQL)  │

│  (Port 8501)         │└─────────────────┘    └─────────────────┘    └─────────────────┘

└──────────┬───────────┘```

           │

┌──────────▼───────────┐## Core Components

│   Python Modules     │  ← Business Logic

├──────────────────────┤### 1. Web Interface Layer

│ • Document Ingestion │  (core/ingestion.py)

│ • RAG Pipeline       │  (ai_agent/graph.py)**Technology**: Streamlit

│ • Vector Store Mgmt  │  (core/vector_store/)**Purpose**: Provides user-friendly interface for document management and chat

│ • CRUD Operations    │  (database/crud.py)

│ • AI Model Factory   │  (ai_models/)**Components**:

└──────────┬───────────┘- **Main Application** (`app/main.py`): Entry point and navigation

           │- **Chat Interface** (`app/modules/chat.py`): Query interface and response display

      ┌────┴────┐- **Upload Interface** (`app/modules/upload.py`): Document and URL upload

      │         │- **Dashboard** (`app/modules/dashboard.py`): System statistics and monitoring

┌─────▼────┐ ┌─▼──────────┐- **Management Interface** (`app/modules/management.py`): Document and collection management

│PostgreSQL│ │Vector Store│

│(Metadata)│ │(Embeddings)│### 2. RAG Pipeline (LangGraph)

└──────────┘ └────────────┘

  Port 5432   Chroma/Pinecone/pgvector**Technology**: LangGraph, LangChain

```**Purpose**: Orchestrates the multi-stage validation workflow


# KnowledgeSavvy Architecture Documentation

## Overview

KnowledgeSavvy is a Retrieval-Augmented Generation (RAG) system with a modular, extensible design. It uses Streamlit for the UI, LangGraph for orchestration, and factory-based abstractions for vector stores and LLMs so components can be swapped with minimal code changes.

**Key components**
- Web interface (Streamlit)
- RAG pipeline (LangGraph with multi-stage validation)
- Document processing (multi-format ingestion and chunking)
- Vector storage (Chroma, Pinecone, pgvector via factory)
- Database (PostgreSQL for metadata)

## High-Level Architecture

Streamlit UI ↔ LangGraph RAG pipeline ↔ Vector store (Chroma/Pinecone/pgvector) ↔ PostgreSQL metadata

## Core Components

### 1. Web Interface Layer (`app/`)
- Technology: Streamlit
- Purpose: User-facing pages for chat, uploads, dashboard, and management
- Entry point: `app/main.py`
- Modules: `modules/chat.py`, `modules/upload.py`, `modules/dashboard.py`, `modules/management.py`

### 2. RAG Pipeline Layer (`ai_agent/`)
- Technology: LangGraph, LangChain
- Entry point: `ai_agent/graph.py`
- Nodes: retrieve → grade_documents → generate → validate → web_search (fallback)
- Validation: relevance grading, hallucination check, answer quality check

### 3. Document Processing Layer (`core/`)
- Technology: LangChain loaders, Unstructured, PyPDF
- Responsibilities: load, extract, chunk, and index documents
- Key module: `core/ingestion.py`

### 4. Vector Store Layer (`core/vector_store/`)
- Technology: Chroma, Pinecone, pgvector
- Factory: `core/vector_store/vs_factory.py` selects backend via config
- Manager: `core/vector_store/vs_manager.py` unified operations (add, search, delete)

### 5. AI Models Layer (`ai_models/`)
- Factory pattern for embeddings and LLMs
- Configurable in `ai_models/config.py`; creation in `ai_models/mdl_factory.py`
- Current defaults: Cohere for generation/embeddings, Gemini for grading/validation

### 6. Database Layer (`database/`)
- Technology: PostgreSQL + SQLAlchemy
- Purpose: metadata and relationships (collections, sources, document IDs)
- Modules: `database/models.py`, `database/crud.py`

## Data Flows

**Document upload**: Upload → processing → chunking → embedding → vector store → metadata DB update

**Query processing**: Query → retrieval → grading → generation → validation → (optional web search) → response

## Modularity and Extensibility

- **Vector stores**: switch via `VECTOR_STORE_BACKEND` and factory; add new backends by implementing the interface used in `vs_manager.py`.
- **Models**: swap providers/models in `ai_models/config.py`; factories decouple tasks (generation, embeddings, grading, validation).
- **Loaders**: format-specific loaders can be extended in `core/ingestion.py`.

## Validation Pipeline (LangGraph)

1) Retrieve
2) Grade documents (relevance)
3) Generate answer
4) Validate (hallucination + quality)
5) Web search fallback if needed

## Score Semantics
- `relevance_score` (0–1): Assigned by the LLM grader for retrieved documents; for web results it is provided by Tavily (`tavily_result["score"]`). Higher means more relevant.
- `similarity_score` (backend-specific): Returned by the vector store (`similarity_search_with_score`); interpret it comparatively within the same result set (cosine similarity or distance depending on backend).

## Deployment Scope

Current scope is local/dev (Streamlit + Dockerized PostgreSQL/pgvector). Production deployment (cloud/K8s/load balancing) is out of scope for this version.
                ├─ 1:N → DocumentsIds (id, doc_id, source_id)

```- **Document Counts**: Per collection and total

- **Processing Times**: Upload and indexing metrics

**CRUD Operations** (`database/crud.py`):- **Quality Scores**: Relevance and validation scores

- **Error Tracking**: Comprehensive error logging

**Session Management**:

```python## Deployment Architecture

@db_operation("operation_name", read_only=False)

def operation(session, ...):### Container Strategy

    # Session automatically managed

    # Commits on success, rollbacks on error- **Application**: Python application with dependencies

    # Closes after execution- **Database**: PostgreSQL with pgvector extension

```- **Vector Store**: Configurable backend selection



**Operations**:### Environment Support

- Collections: create, get_all, delete

- Sources: create_and_link, get_by_collection, delete- **Development**: Local development with Chroma

- Document IDs: get_by_source- **Staging**: PostgreSQL with pgvector

- **Production**: Pinecone or PostgreSQL with pgvector

---

## Testing Architecture

## Data Flow

### Test Strategy

### Document Upload Flow

**Test Framework**: pytest with comprehensive fixture system

```**Test Database**: SQLite in-memory for unit tests (fast, isolated)

User Upload → DocumentProcessor.load_document()**Mocking Strategy**: Mock external dependencies (APIs, vector stores, LLMs)

                ↓

            Split into chunks (RecursiveCharacterTextSplitter)### Test Coverage

                ↓

            Generate embeddings (EmbeddingModelFactory)- **Unit Tests** (27 tests): Fast, isolated, no external dependencies

                ↓  - Database CRUD operations (10 tests)

            Store in vector store (VectorStoreManager.add_documents)  - Vector store manager (10 tests)

                ↓  - Configuration and logging (7 tests)

            Save metadata to DB (crud.create_source_and_add_to_collection)  

                ↓- **Integration Tests** (1 test): Complete workflow validation

            Return chunk count  - Document add-search-delete workflow

```

### Key Testing Patterns

### Query Processing Flow

1. **Database Session Management**: Use `@db_operation` decorator with direct DB queries in tests

```2. **Mock Patching**: Patch at usage point (`vs_manager.get_vectorstore` not `vs_factory.get_vectorstore`)

User Question → RAG Pipeline (ai_agent/graph.py)3. **Fixture Composition**: Combine fixtures for complex test scenarios

                  ↓4. **Marker-based Execution**: Selective test execution via pytest markers

              [1] RETRIEVE

                  ├─ VectorStoreManager.similarity_search(k=4)For detailed testing information, see [tests/README.md](../tests/README.md).

                  └─ Returns: List[Document]

                  ↓## Future Enhancements

              [2] GRADE_DOCUMENTS

                  ├─ Document Grading Model scores relevance### Planned Features

                  └─ Filter: Keep documents with score ≥ 8/10

                  ↓- **Multi-language Support**: Internationalization

              [3] GENERATE
                  ├─ Generator Model creates answer
                  ├─ Input: question + relevant_docs + chat_history
                  └─ Returns: Generated answer
                  ↓
              [4] VALIDATE
                  ├─ Hallucination Grader: Is answer grounded?
                  ├─ Answer Grader: Does it address question?
                  └─ Decision: Pass/Retry/Web Search
                  ↓
              [5] Optional: WEB_SEARCH (if validation fails or no relevant docs)
                  ├─ Tavily API search
                  ├─ Generate from web results
                  └─ Returns: Answer + web sources
                  ↓
              Return: Final answer + sources
```

---

## Configuration System

### Environment-Based Configuration (`config/settings.py`)

**Pydantic Settings** with `.env` file:

```python
class AppSettings(BaseSettings):
    # Database
    postgres_user: str
    postgres_password: str
    postgres_server: str
    postgres_db: str
    database_url: Optional[str]  # Override for composed URL
    
    # Vector Store
    vector_store_backend: str = "chroma"
    chroma_persist_dir: str = "data/vector_stores_db/chroma_store"
    
    # API Keys
    google_api_key: Optional[str]
    cohere_api_key: Optional[str]
    tavily_api_key: Optional[str]
    pinecone_api_key: Optional[str]
    
    # Logging
    debug: bool = False
    
    @property
    def resolved_database_url(self) -> str:
        return self.database_url or f"postgresql+psycopg://{self.postgres_user}:..."
```

**Singleton Pattern**:
```python
@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()

settings = get_settings()  # Global instance
```

### SSL Configuration (`config/ssl_config.py`)

```python
def configure_ssl():
    """Set SSL certificate paths for HTTPS requests."""
    cert_path = certifi.where()
    os.environ["SSL_CERT_FILE"] = cert_path
    os.environ["REQUESTS_CA_BUNDLE"] = cert_path
```

---

## Testing Architecture

### Test Strategy

**Framework**: pytest  
**Isolation**: SQLite in-memory for unit tests  
**Mocking**: External dependencies (APIs, vector stores)

**Test Structure**:
```
tests/
├── conftest.py          # Shared fixtures
├── test_crud.py         # Database operations (10 tests)
├── test_vs_manager.py   # Vector store manager (11 tests)
└── test_config.py       # Configuration (7 tests)
```

**Fixtures**:
- `temp_db` - SQLite in-memory database
- `mock_vector_store` - Mocked Chroma vectorstore
- `mock_embedding` - Mocked embedding model
- `mock_vs_config` - Mocked vector store configuration

**Markers**:
- `@pytest.mark.unit` - Fast, isolated tests
- `@pytest.mark.integration` - Complete workflow tests
- `@pytest.mark.database` - Real PostgreSQL tests (not implemented)

### Key Testing Patterns

**Database Session Management**:
```python
# CRUD decorator closes session automatically
crud.create_collection("name", "desc")

# Test must query DB directly
collection = temp_db.query(models.Collection).filter_by(name="name").first()
assert collection.name == "name"
```

**Mock Patching**:
```python
# Patch at usage point, not definition
with patch('core.vector_store.vs_manager.get_vectorstore', return_value=mock):
    manager = VectorStoreManager(config, embedding)
```

---

## Security Considerations

### Input Validation

- Collection names: Regex `^[a-z0-9-]+$`
- File types: Whitelist (PDF, TXT, DOCX, MD, CSV)
- File size: Streamlit default limits
- SQL injection: SQLAlchemy ORM (parameterized queries)

### API Key Management

- Stored in `.env` (not committed to git)
- Loaded via Pydantic Settings
- Never logged or exposed in UI
- Separate keys for dev/prod recommended

### Database Security

- Password authentication required
- Connections through Docker network (not exposed externally)
- User permissions via SQLAlchemy (no raw SQL)

---

## Logging System

### Centralized Configuration (`core/logger.py`)

**Auto-configured on import**:
```python
setup_logging()  # Called automatically
logger = logging.getLogger(__name__)
```

**Features**:
- **File Handler**: Rotating logs (10MB, 5 backups)
- **Console Handler**: Colored output (development)
- **JSON Format**: Structured logs (file)
- **Dynamic Level**: DEBUG if `DEBUG=true`, else INFO

**Log Locations**:
- Files: `data/logs/KnowledgeSavvy.log`
- Console: Streamlit terminal output

---

## Performance Characteristics

### Document Processing

- **Chunk Size**: 4000 characters (configurable)
- **Overlap**: 200 characters (configurable)
- **Batch Processing**: Automatic based on token count
- **Embedding**: ~0.5s per batch (Cohere API)

### Query Performance

- **Vector Search**: <100ms (Chroma local), <200ms (Pinecone)
- **Document Grading**: ~1s for 4 documents
- **Answer Generation**: ~2-4s (depends on context length)
- **Total RAG Pipeline**: ~4-7s per query

### Database Performance

- **Collection Listing**: <10ms
- **Source Creation**: <50ms
- **Document ID Insertion**: Batch operation, ~100ms for 1000 IDs

---

## Scalability Considerations

### Current Limitations

- **Single Streamlit Instance**: No load balancing
- **Sequential Processing**: One request at a time
- **Local Vector Store**: Chroma not suitable for >1M documents

### Scalability Improvements (Not Implemented)

- Multi-instance Streamlit deployment
- Async document processing (Celery/RQ)
- Production vector store (Pinecone/pgvector)
- Database connection pooling
- Caching layer (Redis)

---

## Technology Stack Summary

| Layer                | Technology           | Purpose                      |
|----------------------|----------------------|------------------------------|
| Web Interface        | Streamlit            | UI and user interaction      |
| Workflow Orchestration | LangGraph          | RAG pipeline state machine   |
| AI Framework         | LangChain            | Document processing, chains  |
| Embedding Model      | Cohere               | Text vectorization           |
| LLM Models           | Cohere + Gemini      | Generation and validation    |
| Vector Store         | Chroma/Pinecone/pgvector | Similarity search      |
| Database             | PostgreSQL           | Metadata storage             |
| ORM                  | SQLAlchemy           | Database abstraction         |
| Configuration        | Pydantic Settings    | Environment management       |
| Testing              | pytest               | Unit and integration tests   |
| Containerization     | Docker Compose       | PostgreSQL deployment        |
| Dependency Management| Pipenv               | Python package management    |

---

## Design Patterns

### Factory Pattern
- **Model Factories**: `EmbeddingModelFactory`, `LlmModelFactory`
- **Vector Store Factory**: `get_vectorstore()`
- Benefits: Centralized creation, easy to extend

### Singleton Pattern
- **Settings**: `@lru_cache` for single instance
- Benefits: Consistent configuration across modules

### Decorator Pattern
- **Database Operations**: `@db_operation`
- Benefits: Automatic session management, error handling

### Strategy Pattern
- **Vector Store Backends**: Unified interface, multiple implementations
- Benefits: Easy backend switching, consistent API

---

## Architecture Achievements

This architecture demonstrates several software engineering best practices:

✅ **Modular Design** - Clean separation between UI, business logic, and data layers  
✅ **Design Patterns** - Factory, Singleton, Decorator, and Strategy patterns  
✅ **Scalability Considerations** - Abstraction layer allows easy backend switching  
✅ **Testing Architecture** - Comprehensive test fixtures and mocking strategy  
✅ **Configuration Management** - Environment-based settings with Pydantic  
✅ **Error Handling** - Decorator pattern for automatic session management  
✅ **Type Safety** - Type hints throughout for better IDE support and documentation  

### Scope Note

This is a **local development application** focused on demonstrating RAG implementation and clean Python architecture. Production features like REST APIs, authentication, Kubernetes deployment, and horizontal scaling are intentionally not included to maintain focus on core RAG functionality and code quality.
