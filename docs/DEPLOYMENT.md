# KnowledgeSavvy Deployment Guide

## Overview

This guide covers **local development deployment** for KnowledgeSavvy. The application is designed as a Streamlit web interface with PostgreSQL database backend for personal or team use.

**Current Scope**: Local development environment only. Production deployment infrastructure (cloud hosting, Kubernetes, load balancing, etc.) is not implemented in this version.

---

## Prerequisites

### System Requirements

- **Python**: 3.13 or higher
- **Memory**: Minimum 4GB RAM, recommended 8GB+
- **Storage**: Minimum 10GB free space
- **Network**: Internet access for AI model APIs and package installation

### Required Software

- **Python 3.13+** - Core runtime
- **Pipenv** - Dependency and virtual environment management
- **Docker & Docker Compose** - For PostgreSQL database
- **Git** - Source code management

### Required API Keys

You'll need accounts and API keys for:

- **Google AI (Gemini)** - For document grading and validation ([Get API key](https://ai.google.dev/))
- **Cohere** - For embeddings and text generation ([Get API key](https://cohere.com/))
- **Tavily** - For web search functionality (optional) ([Get API key](https://tavily.com/))
- **Pinecone** - If using Pinecone vector store (optional) ([Get API key](https://www.pinecone.io/))

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/KnowledgeSavvy.git
cd KnowledgeSavvy
```

### 2. Install Pipenv

```bash
pip install pipenv
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev/test dependencies
pipenv install --dev
```

This creates a virtual environment and installs all required packages defined in `Pipfile`.

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy example file
cp .env.example .env

# Edit with your configuration
# On Windows: notepad .env
# On Linux/Mac: nano .env
```

**Required Environment Variables**:

```ini
# Database Configuration
POSTGRES_USER=knowledgesavvy_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=knowledgesavvy

# AI Model API Keys
GOOGLE_API_KEY=your_google_api_key_here
COHERE_API_KEY=your_cohere_api_key_here

# Optional: Web Search
TAVILY_API_KEY=your_tavily_api_key_here

# Vector Store Configuration
VECTOR_STORE_BACKEND=chroma  # Options: chroma, pinecone, pgvector

# Optional: Pinecone Configuration (if using Pinecone)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX=your_pinecone_index_name

# Optional: Chroma Configuration (default)
CHROMA_PERSIST_DIR=data/vector_stores_db/chroma_store

# Optional: LangSmith (tracing and observability - not required)
LANGCHAIN_TRACING_V2=false  # Set to true to enable tracing
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=your_project_name

# Optional: Logging
DEBUG=false  # Set to true for debug logging
```

**Security Note**: Never commit the `.env` file to version control. It's already in `.gitignore`.

---

## Database Setup

### Using Docker Compose (Recommended)

The project includes a `docker-compose.yml` file for PostgreSQL with pgvector extension.

**Start PostgreSQL**:

```bash
docker compose up -d postgres_kns
```

**Verify Database is Running**:

```bash
docker compose ps
```

You should see the postgres_kns container running on port 5432.

**View Database Logs**:

```bash
docker compose logs postgres_kns
```

**Stop Database**:

```bash
docker compose down
```

### Manual PostgreSQL Setup (Alternative)

If you prefer to install PostgreSQL manually:

1. **Install PostgreSQL 15+** with pgvector extension
2. **Create Database**:

```sql
CREATE DATABASE <your_postgres_db>;
CREATE USER <your_postgres_user> WITH PASSWORD '<your_password>';
GRANT ALL PRIVILEGES ON DATABASE <your_postgres_db> TO <your_postgres_user>;
```

3. **Install pgvector Extension**:

```sql
\c knowledgesavvy
CREATE EXTENSION IF NOT EXISTS vector;
```

4. **Update `.env`** with your PostgreSQL connection details

---

## Running the Application

### Start the Application

**Always activate the virtual environment first**:

```bash
# Activate pipenv shell
pipenv shell

# Run Streamlit application
streamlit run app/main.py
```

The application will start on **http://localhost:8501** by default.

**Alternative (without activating shell)**:

```bash
pipenv run streamlit run app/main.py
```

### Accessing the Application

Open your browser and navigate to:

```
http://localhost:8501
```

You should see the KnowledgeSavvy interface with:
- Chat interface
- Document upload
- Dashboard
- Document management

---

## Testing

### Run All Unit Tests

```bash
# Activate environment
pipenv shell

# Run all unit tests (fast, uses SQLite in-memory)
python -m pytest tests/ -m unit -v

# Run specific test file
python -m pytest tests/test_crud.py -v

# Run with coverage
python -m pytest --cov=. --cov-report=html
```

### Test Organization

- **Unit Tests**: Fast, isolated tests with mocked dependencies
- **Integration Tests**: End-to-end tests with real database (not implemented yet)

For detailed testing documentation, see [docs/TESTING.md](TESTING.md).

---

## Vector Store Configuration

### Chroma (Local, Default)

**Advantages**:
- No additional setup required
- Free and open-source
- Good for development and small datasets

**Configuration**:

```ini
VECTOR_STORE_BACKEND=chroma
CHROMA_PERSIST_DIR=data/vector_stores_db/chroma_store
```

**Data Location**: All vector data is stored locally in the specified directory.

### Pinecone (Cloud)

**Advantages**:
- Scalable cloud solution
- Fast similarity search
- Good for large datasets

**Configuration**:

```ini
VECTOR_STORE_BACKEND=pinecone
PINECONE_API_KEY=your_api_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX=your_index_name
```

**Setup**:
1. Create account at [Pinecone](https://www.pinecone.io/)
2. Create an index with 1024 dimensions (for Cohere embeddings)
3. Copy API key and environment details to `.env`

### pgvector (PostgreSQL)

**Advantages**:
- Single database for metadata and vectors
- No additional infrastructure
- Good for moderate datasets

**Configuration**:

```ini
VECTOR_STORE_BACKEND=pgvector
# Uses same PostgreSQL connection as metadata
```

**Requirements**:
- PostgreSQL with pgvector extension (included in Docker setup)
- No additional configuration needed

---

## Database Management

### View Database Schema

```bash
# Connect to database (service name 'postgres_kns' from docker-compose.yml)
docker compose exec postgres_kns psql -U <your_postgres_user> -d <your_postgres_db>

# List tables
\dt

# Describe table
\d collections
\d sources
\d documents_ids

# Exit
\q
```

### Backup Database

```bash
# Backup database
docker compose exec postgres_kns pg_dump -U <your_postgres_user> <your_postgres_db> > backup.sql

# Restore database
docker compose exec -i postgres_kns psql -U <your_postgres_user> <your_postgres_db> < backup.sql
```

### Reset Database

```bash
# Drop all tables and recreate
docker compose exec postgres_kns psql -U <your_postgres_user> -d <your_postgres_db> -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

**Warning**: This will delete ALL data. Make sure to backup first.

---

## Troubleshooting

### Common Issues

#### Port Already in Use

**Error**: `Address already in use: localhost:8501`

**Solution**:
```bash
# Find process using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

#### PostgreSQL Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solutions**:
1. Verify Docker container is running: `docker compose ps`
2. Check PostgreSQL logs: `docker compose logs postgres_kns`
3. Verify connection details in `.env` match `docker-compose.yml`
4. Try restarting container: `docker compose restart postgres_kns`

#### Missing API Keys

**Error**: `API key not found` or `Unauthorized`

**Solutions**:
1. Verify `.env` file exists in project root
2. Check API keys are correct and active
3. Ensure `.env` variables match required names exactly
4. Restart application after changing `.env`

#### Import Errors

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solutions**:
1. Verify virtual environment is activated: `pipenv shell`
2. Reinstall dependencies: `pipenv install --dev`
3. Check Python version: `python --version` (should be 3.13+)

#### Vector Store Issues

**Chroma Errors**:
- Delete and recreate: Remove `data/vector_stores_db/chroma_store` directory
- Check disk space
- Verify file permissions

**Pinecone Errors**:
- Verify API key is valid
- Check index exists and has correct dimensions (1024)
- Verify environment name is correct

**pgvector Errors**:
- Ensure pgvector extension is installed: `CREATE EXTENSION IF NOT EXISTS vector;`
- Check PostgreSQL version (15+)
- Verify database connection

---

## Development Workflow

### Recommended Workflow

1. **Start Database**:
   ```bash
   docker compose up -d postgres_kns
   ```

2. **Activate Environment**:
   ```bash
   pipenv shell
   ```

3. **Run Tests** (optional but recommended):
   ```bash
   python -m pytest tests/ -m unit -v
   ```

4. **Start Application**:
   ```bash
   streamlit run app/main.py
   ```

5. **Develop**: Make changes, test in browser

6. **Stop Everything**:
   - Ctrl+C to stop Streamlit
   - `docker compose down` to stop database
   - `exit` to leave pipenv shell

### Making Code Changes

1. **Edit Files**: Make your changes to Python files
2. **Streamlit Auto-Reloads**: Save file and click "Rerun" in browser
3. **Test Changes**: Run relevant pytest tests
4. **Check Logs**: View `data/logs/KnowledgeSavvy.log` for errors

### Adding New Dependencies

```bash
# Add new package
pipenv install package_name

# Add dev dependency
pipenv install --dev package_name

# Update Pipfile.lock
pipenv lock
```

---

## Project Structure

```
KnowledgeSavvy/
├── app/                    # Streamlit web interface
│   ├── main.py            # Entry point
│   └── modules/           # UI modules (chat, upload, etc.)
├── ai_agent/              # LangGraph RAG pipeline
│   ├── graph.py           # Workflow definition
│   ├── chains/            # LLM chains
│   └── nodes/             # Workflow nodes
├── ai_models/             # AI model factories
│   ├── mdl_factory.py     # Model creation
│   └── config.py          # Model configuration
├── core/                  # Business logic
│   ├── ingestion.py       # Document processing
│   ├── logger.py          # Logging setup
│   └── vector_store/      # Vector store abstraction
├── database/              # Database layer
│   ├── models.py          # SQLAlchemy models
│   ├── crud.py            # CRUD operations
│   └── connection.py      # DB connection
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest fixtures
│   └── test_*.py          # Test files
├── data/                  # Runtime data
│   ├── logs/              # Application logs
│   └── vector_stores_db/  # Local vector stores
├── docs/                  # Documentation
├── .env                   # Environment variables (create this)
├── docker-compose.yml     # PostgreSQL setup
├── Pipfile                # Dependencies
└── README.md              # Project overview
```

---

## Monitoring and Logs

### Application Logs

Logs are written to `data/logs/KnowledgeSavvy.log` with automatic rotation (10MB max, 5 backups).

**View Logs**:

```bash
# Tail logs (real-time)
tail -f data/logs/KnowledgeSavvy.log

# View last 100 lines
tail -n 100 data/logs/KnowledgeSavvy.log

# Search for errors
grep ERROR data/logs/KnowledgeSavvy.log
```

**Log Levels**:
- **DEBUG**: Detailed information for debugging (set `DEBUG=true` in `.env`)
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

### Database Logs

```bash
# PostgreSQL logs
docker compose logs -f postgres_kns

# Last 50 lines
docker compose logs --tail=50 postgres_kns
```

---

## Performance Optimization

### Document Processing

- **Chunk Size**: Default 4000 characters, adjust based on document type
- **Batch Size**: Automatically calculated based on token count
- **Parallel Processing**: Not implemented yet

### Query Performance

- **Vector Store**: Pinecone > pgvector > Chroma for large datasets
- **Embedding Cache**: Not implemented yet
- **Database Indexing**: Automatically handled by SQLAlchemy

### Resource Management

- **Memory**: 8GB RAM recommended for processing large documents
- **Disk Space**: Monitor vector store size in `data/vector_stores_db/`
- **Database**: PostgreSQL uses default configuration, tune for production

---

## Security Considerations

### API Key Security

- **Never commit `.env` to git** (already in `.gitignore`)
- **Use strong PostgreSQL passwords**
- **Rotate API keys regularly**
- **Limit API key permissions** when possible

### Network Security

- **Streamlit runs on localhost by default** (port 8501)
- **PostgreSQL exposed only to localhost** in Docker setup
- **No authentication layer** in current version (single-user application)

### Data Privacy

- **Documents stored locally** (Chroma) or in your accounts (Pinecone)
- **API calls to external services**: Google, Cohere, Tavily
- **No data sharing** with third parties beyond API providers
- **Database contains metadata only** (not document content)

---

## Updating the Application

### Update Dependencies

```bash
# Update all packages to latest versions
pipenv update

# Update specific package
pipenv update package_name

# Check for outdated packages
pipenv update --outdated
```

### Pull Latest Code

```bash
# Pull from git
git pull origin main

# Install any new dependencies
pipenv install --dev

# Restart application
```

---

## Uninstalling

### Remove Application

```bash
# Stop database
docker compose down -v  # -v removes volumes

# Remove virtual environment
pipenv --rm

# Delete project directory
cd ..
rm -rf KnowledgeSavvy
```

### Clean Up Data

```bash
# Remove vector stores
rm -rf data/vector_stores_db/

# Remove logs
rm -rf data/logs/
```

---

## Deployment Scope

This guide covers **local development deployment** for KnowledgeSavvy, which is designed as a:

✅ **Development-Ready Application** - Quick setup with pipenv and Docker Compose  
✅ **Fully Functional RAG System** - Complete pipeline with validation stages  
✅ **Flexible Configuration** - Support for multiple vector store backends  
✅ **Comprehensive Testing** - 28 unit tests verify functionality  
✅ **Production-Quality Code** - Type hints, error handling, and logging  

**Design Philosophy**: Focus on clean architecture and core RAG functionality rather than enterprise deployment features. This makes the codebase easier to understand, test, and showcase as a portfolio project.

---

## Getting Help

- **Documentation**: Check `docs/` folder for detailed guides
- **Logs**: Review `data/logs/KnowledgeSavvy.log` for errors
- **GitHub Issues**: Check project repository for known issues
- **API Docs**: See [docs/API.md](API.md) for internal API reference
- **Architecture**: See [docs/ARCHITECTURE.md](ARCHITECTURE.md) for system design

---

## Summary

This guide covered local development deployment for KnowledgeSavvy:

✅ **Prerequisites**: Python 3.13, Pipenv, Docker, API keys  
✅ **Installation**: Clone, install dependencies, configure environment  
✅ **Database**: PostgreSQL with Docker Compose  
✅ **Running**: Streamlit on localhost:8501  
✅ **Testing**: Comprehensive pytest suite  
✅ **Configuration**: Vector stores (Chroma/Pinecone/pgvector)  
✅ **Troubleshooting**: Common issues and solutions  
✅ **Development**: Recommended workflow and best practices  

For production deployment, you would need to implement additional infrastructure, security, and scalability features not covered in this guide.
