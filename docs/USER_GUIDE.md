# KnowledgeSavvy User Guide

## Welcome to KnowledgeSavvy

KnowledgeSavvy is an intelligent document management and question-answering system that helps you organize, search, and interact with your knowledge base. This guide will walk you through all the features and help you get the most out of the system.

## Getting Started

### First Time Setup

Before accessing the system, ensure you have:
1. **Configured your environment**: Create a `.env` file following the template in `.env.example`
2. **Set up API keys**: Add your Google, Cohere, and Tavily API keys to `.env`
3. **Started the database**: Run `docker compose up -d postgres_kns` to start PostgreSQL

Once configured:
1. **Access the System**: Open your web browser and navigate to `http://localhost:8501`
2. **Create Your First Collection**: Start by creating a collection to organize your documents
3. **Upload Documents**: Add your first documents to begin building your knowledge base
4. **Start Chatting**: Ask questions about your documents and get intelligent answers

### System Overview

The KnowledgeSavvy interface is organized into four main sections:
- **💬 Chat**: Ask questions and get answers from your knowledge base
- **📤 Upload Documents**: Add new documents and URLs to your collections
- **📊 Dashboard**: View statistics and monitor your knowledge base
- **🗂️ Manage Documents**: Organize and maintain your documents

## Collections Management

### What are Collections?

Collections are logical groupings that help you organize your documents by topic, project, or any other meaningful category. Think of them as folders that contain related documents.

### Creating a Collection

1. **Navigate to the Sidebar**: Look for the "📁 Topic Management" section on the left
2. **Click "➕ New Topic"**: This will expand the collection creation form
3. **Enter Collection Name**: Use lowercase letters, numbers, and hyphens only
   - ✅ Good examples: `machine-learning`, `project-2024`, `research-papers`
   - ❌ Bad examples: `Machine Learning`, `Project 2024`, `Research Papers`
4. **Add Description** (Optional): Provide context about what this collection contains
5. **Click "Create Collection"**: Your new collection will be created and appear in the selector

### Collection Naming Rules

- **Allowed characters**: Lowercase letters (a-z), numbers (0-9), hyphens (-)
- **Cannot start or end with a hyphen**
- **Must be unique** across your entire system
- **Examples**: `ai-research`, `company-docs-2024`, `technical-manuals`

### Managing Collections

- **Select a Collection**: Use the dropdown in the sidebar to switch between collections
- **View Collection Info**: See document count, creation date, and description
- **Delete Collection**: Use the management interface to remove collections (this will delete all documents within)

## Document Upload

### Supported File Types

KnowledgeSavvy supports a wide range of document formats:

- **PDF Documents** (.pdf): Text-based PDFs with automatic text extraction
- **Word Documents** (.docx): Microsoft Word documents
- **Text Files** (.txt): Plain text files
- **Markdown Files** (.md): Markdown-formatted documents
- **CSV Files** (.csv): Comma-separated value files

### Uploading Files

1. **Select Collection**: Make sure you have a collection selected
2. **Go to Upload Tab**: Click on "📤 Upload Documents"
3. **Choose File Type**: Select "Document" for file uploads
4. **Configure Settings**:
   - **Chunk Size**: How large each text segment should be (1000-10000 characters)
   - **Chunk Overlap**: How much text should overlap between chunks (0-500 characters)
5. **Select Files**: Click "Browse files" and select one or more documents
6. **Review Files**: Check the file previews to ensure correct selection
7. **Process Documents**: Click "🚀 Process and Vectorize" to start processing

### Chunking Configuration

**Chunk Size**: Determines how your documents are split into searchable pieces
- **Smaller chunks** (1000-2000): More precise answers, more chunks to manage
- **Larger chunks** (4000-8000): Better context, fewer chunks
- **Recommended**: Start with 4000 characters for most documents

**Chunk Overlap**: Ensures important information isn't lost at chunk boundaries
- **No overlap** (0): Clean separation, may miss context
- **Some overlap** (100-200): Good balance of context and efficiency
- **High overlap** (300-500): Maximum context, more storage required

### Web Scraping

In addition to file uploads, you can also add web content:

1. **Select "URL"**: Choose URL processing instead of file upload
2. **Enter URL**: Provide the website address you want to scrape
3. **Set Scraping Depth**: Choose how many levels deep to crawl (1-5)
   - **Depth 1**: Just the main page
   - **Depth 2-3**: Main page + linked pages
   - **Depth 4-5**: Extensive crawling (use sparingly)
4. **Click "📥 Upload URL"**: The system will crawl and process the website

### Processing Status

During document processing, you'll see:
- **Progress Bar**: Shows overall completion percentage
- **Status Messages**: Indicates which file is being processed
- **Success Messages**: Confirms when documents are completed
- **Error Handling**: Alerts if any issues occur during processing

## Chat Interface

### Asking Questions

1. **Select Collection**: Choose the collection containing relevant documents
2. **Go to Chat Tab**: Click on "💬 Chat"
3. **Type Your Question**: Use natural language to ask about your documents
4. **Press Enter**: The system will process your question and provide an answer

### Question Examples

**General Questions**:
- "What is machine learning?"
- "Explain the main concepts in the document"
- "Summarize the key points"

**Specific Questions**:
- "What does the document say about neural networks?"
- "How is data preprocessing described?"
- "What are the main challenges mentioned?"

**Comparative Questions**:
- "How do the approaches differ between documents?"
- "What are the similarities between these concepts?"

### Understanding Responses

Each response includes:
- **Main Answer**: The AI-generated response to your question
- **Source Documents**: Which documents were used to generate the answer
- **Relevance Scores (0–1)**: Relevance to your question on a 0–1 scale
   - For retrieved documents: produced by the LLM grader (structured output)
   - For web results: provided by Tavily as `tavily_result["score"]`
- **Similarity Score (backend-specific)**: Numeric score returned by the vector store (`similarity_search_with_score`)
   - This value is backend-dependent (e.g., cosine similarity or distance). Use it comparatively within the same result set.
- **Web Search Integration**: Whether additional web information was used

### Response Quality

- Relevance scores close to 1.0 indicate higher relevance; near 0.0 indicate low relevance.
- Similarity scores are backend-specific and should be interpreted relatively across the retrieved set.

Note: The RAG pipeline includes validation stages that filter out irrelevant documents before generating answers.

### Viewing Sources

1. **Expand Sources**: Click "📚 View sources and details" below any response
2. **Review Documents**: See which specific documents were used
3. **Check Relevance Scores**: Understand how relevant each source was
4. **Verify Information**: Cross-reference with original documents if needed

## Dashboard and Analytics

### Overview Metrics

The dashboard provides key insights about your knowledge base:

- **Collections**: Total number of collections you've created
- **Total Documents**: Combined document count across all collections
- **Document Distribution**: Visual representation of documents per collection

### Collection Details

For each collection, you can see:
- **Name and Description**: Collection identification and purpose
- **Document Count**: How many documents are in the collection
- **Creation Date**: When the collection was established
- **Source Breakdown**: Types and counts of different document sources

### Source Information

Each source shows:
- **Title**: Document name or URL
- **Type**: File format or source type
- **Upload Date**: When it was added to the system
- **Chunk Count**: How many text segments were created

## Document Management

### Viewing Documents

1. **Go to Management Tab**: Click on "🗂️ Manage Documents"
2. **Browse Collections**: See all your collections and their contents
3. **Expand Sources**: Click on collection names to see individual documents
4. **Review Metadata**: Check document types, upload dates, and descriptions

### Deleting Individual Documents

1. **Select Collection**: Choose the collection containing the document
2. **Choose Document**: Pick the specific document to remove
3. **Confirm Deletion**: Check the confirmation box
4. **Click Delete**: Remove the document from your knowledge base

**Note**: This action cannot be undone. The document and all its chunks will be permanently removed.

### Deleting Collections

1. **Go to Collection Deletion**: Use the second tab in the management interface
2. **Select Collection**: Choose the collection to remove
3. **Review Impact**: See how many documents will be deleted
4. **Double Confirm**: Check both confirmation boxes
5. **Delete Collection**: Remove the entire collection and all its contents

**Warning**: This will delete ALL documents in the collection. Use with extreme caution.

## Best Practices

### Document Organization

- **Use Descriptive Names**: Create collections with clear, meaningful names
- **Group Related Content**: Put similar documents in the same collection
- **Limit Collection Size**: Don't put too many documents in a single collection
- **Regular Maintenance**: Periodically review and clean up old collections

### Question Asking

- **Be Specific**: Ask targeted questions for better answers
- **Use Natural Language**: Write questions as you would ask a person
- **Break Down Complex Questions**: Ask multiple simple questions instead of one complex one
- **Verify Important Information**: Always check sources for critical information

### File Management

- **Quality Over Quantity**: Upload well-formatted, relevant documents
- **Consistent Naming**: Use consistent file naming conventions
- **Regular Updates**: Keep your knowledge base current with new information
- **Backup Important Documents**: Maintain copies of critical documents elsewhere

## Troubleshooting

### Common Issues

**Document Not Processing**
- Check file format is supported
- Ensure file isn't corrupted
- Verify collection is selected
- Check system logs for errors

**Poor Answer Quality**
- Verify documents are relevant to your question
- Check if documents were processed correctly
- Try asking more specific questions
- Review source documents for accuracy

**System Slow Performance**
- Reduce chunk overlap settings
- Process documents in smaller batches
- Check available system resources
- Consider using a different vector store backend

### Getting Help

- **Check Logs**: Review system logs at `data/logs/KnowledgeSavvy.log` for error messages
- **Verify Configuration**: Ensure all environment variables in `.env` are set correctly
- **Test with Simple Documents**: Try uploading basic text files first
- **Review Documentation**: Check `docs/DEPLOYMENT.md` for setup troubleshooting
- **Check GitHub Issues**: Visit the project repository for known issues and solutions

## Advanced Features

### Custom Chunking

For specialized documents, you can adjust chunking parameters:
- **Technical Documents**: Use larger chunks (6000-8000) for complex concepts
- **Simple Text**: Use smaller chunks (2000-3000) for straightforward content
- **Mixed Content**: Use medium chunks (4000-5000) for general documents

### Web Search Integration

When documents are insufficient, the system automatically:
- Searches the web for additional information
- Integrates web content with your documents
- Provides enhanced answers with broader context
- Indicates when web search was used

### Multi-Collection Queries

You can ask questions across multiple collections by:
- Creating comprehensive collections
- Using broad question phrasing
- Leveraging the system's ability to find relevant information

## Security and Privacy

### Data Protection

- **Local Storage**: Documents are stored on your system in the vector store and PostgreSQL database
- **API Key Security**: Your AI provider API keys (Cohere, Google, Pinecone, LangSmith) are stored in `.env` and never logged
- **External API Calls**: The system makes calls to:
  - **Cohere**: For embeddings and text generation
  - **Google Gemini**: For document grading and validation
  - **Tavily**: For web search (optional)
  - **Pinecone**: If using cloud vector store (optional)
  - **LangSmith**: For tracing and observability if `LANGCHAIN_TRACING_V2=true` (optional)
- **No Multi-User Auth**: Current version is single-user local application

**Note on LangSmith**: If you enable LangSmith tracing (`LANGCHAIN_TRACING_V2=true`), execution traces including queries and responses will be sent to LangSmith's servers for debugging and monitoring purposes. This is optional and disabled by default.

### Best Practices

- **Regular Backups**: Keep backups of your PostgreSQL database and vector store data
- **Secure API Keys**: Never commit `.env` file to version control
- **Local Access**: Keep the Streamlit application on localhost (default port 8501)
- **Update Dependencies**: Regularly update Python packages with `pipenv update`
- **Review Logs**: Check `data/logs/KnowledgeSavvy.log` for errors

## Performance Tips

### Optimizing Upload Speed

- **Batch Processing**: Upload multiple documents at once
- **Optimal Chunking**: Use appropriate chunk sizes for your content
- **File Preparation**: Ensure documents are clean and well-formatted
- **System Resources**: Ensure adequate memory and storage

### Improving Query Performance

- **Relevant Collections**: Use collections that match your questions
- **Clear Questions**: Ask specific, well-formed questions
- **Document Quality**: Ensure uploaded documents are relevant and well-formatted
- **Regular Maintenance**: Clean up old or irrelevant documents

## System Capabilities

**KnowledgeSavvy** provides the following features:

✅ **Streamlit Web Interface** - User-friendly interactive application  
✅ **Multi-Format Support** - PDF, DOCX, TXT, MD, CSV, and web scraping  
✅ **Flexible Vector Stores** - Choose between Chroma (local), Pinecone (cloud), or pgvector  
✅ **PostgreSQL Database** - Reliable metadata storage with full ACID compliance  
✅ **Advanced RAG Pipeline** - Multi-stage validation with hallucination detection  
✅ **Web Search Integration** - Tavily integration for enhanced answers  
✅ **Collection Management** - Organize documents by topic or project  
✅ **Source Tracking** - Full visibility into which documents support each answer  

### Application Scope

This is a **local development application** designed for:
- Personal knowledge management
- Research document organization
- Team document repositories (small teams)
- RAG system demonstration and learning

**Design Focus**: Clean code architecture, comprehensive testing, and core RAG functionality rather than enterprise features like authentication, REST APIs, or production deployment infrastructure.

## Conclusion

KnowledgeSavvy is designed to be a powerful yet user-friendly tool for managing and interacting with your knowledge base. By following this guide and exploring the system's capabilities, you'll be able to:

- Organize your documents effectively
- Find information quickly and accurately
- Get intelligent answers to your questions
- Maintain a growing, useful knowledge base

Remember that the system learns and improves as you use it. The more quality documents you add and the more you interact with the system, the better it will serve your needs.

Happy knowledge management!
