# KnowledgeSavvy Documentation

Welcome to the KnowledgeSavvy documentation. This RAG (Retrieval-Augmented Generation) system provides intelligent document processing and question answering with multi-stage validation.

## 📚 Documentation Structure

### For End Users
- **[User Guide](USER_GUIDE.md)** - Complete guide to using the Streamlit web interface
  - Document upload and management
  - Asking questions and understanding responses
  - Collections and organization
  - Troubleshooting

### For Developers
- **[Architecture Overview](ARCHITECTURE.md)** - System design and components
  - High-level architecture
  - RAG pipeline workflow
  - Technology stack
  - Design patterns
  
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Python modules and code structure
  - Database operations (CRUD)
  - Document processing
  - Vector store management
  - AI model factories
  - Usage examples and patterns

- **[Testing Guide](TESTING.md)** - Testing framework and practices
  - Running tests (28 unit tests)
  - Test fixtures and patterns
  - Writing new tests
  - Best practices

- **[Deployment Guide](DEPLOYMENT.md)** - Local development setup
  - Prerequisites and installation
  - Environment configuration
  - Database setup
  - Running the application
  - Troubleshooting

## 🎯 Key Features Implemented

✅ **Multi-Stage RAG Pipeline** - LangGraph workflow with document grading and answer validation  
✅ **Flexible Vector Stores** - Support for Chroma, Pinecone, and pgvector  
✅ **Multi-Format Support** - PDF, DOCX, TXT, MD, CSV, and web scraping  
✅ **Intelligent Validation** - Hallucination detection and answer quality checks  
✅ **Streamlit Web UI** - User-friendly interface for document management  
✅ **Comprehensive Testing** - 28 unit tests with 90%+ coverage  
✅ **Factory Pattern** - Modular AI model management  
✅ **Database Abstraction** - Clean CRUD operations with session management  

## 🚀 Quick Start

1. **Installation**: See [Deployment Guide](DEPLOYMENT.md#installation)
2. **Configuration**: Create `.env` file from `.env.example` template with your API keys
3. **Run Application**: `pipenv shell && streamlit run app/main.py`
4. **Start Using**: Open http://localhost:8501

## 📖 Architecture at a Glance

```
User → Streamlit UI → RAG Pipeline → AI Models
                    ↓
              Vector Store + PostgreSQL
```

**RAG Workflow**: Retrieve → Grade → Generate → Validate → (Web Search if needed)

## 🔧 Technology Stack

- **Backend**: Python 3.13, LangChain, LangGraph
- **AI**: Google Gemini 2.0, Cohere Command
- **Vector Stores**: Chroma / Pinecone / pgvector
- **Database**: PostgreSQL + SQLAlchemy
- **UI**: Streamlit
- **Testing**: pytest (28 tests)

## 📊 Project Statistics

- **Lines of Code**: ~5,000+ (excluding tests)
- **Test Coverage**: 90%+ on core modules
- **Supported Formats**: 5 document types + web scraping
- **Vector Store Backends**: 3 (Chroma, Pinecone, pgvector)
- **AI Models**: 4 (embedding, generation, 2x grading)

## 💡 Development Highlights

- **Clean Architecture**: Separation of concerns (UI, business logic, data)
- **Design Patterns**: Factory, Singleton, Decorator patterns
- **Type Safety**: Type hints throughout codebase
- **Error Handling**: Comprehensive logging and error management
- **Testing**: Unit tests with fixtures and mocks
- **Documentation**: Extensive inline and external docs

## 📞 Need Help?

- **Issues?** Check [Troubleshooting](DEPLOYMENT.md#troubleshooting)
- **Code questions?** See [Developer Guide](DEVELOPER_GUIDE.md)
- **Testing?** Read [Testing Guide](TESTING.md)

---

**Note**: This is a local development application designed for personal or team use. It does not include production deployment infrastructure (REST API, authentication, Kubernetes, etc.).
