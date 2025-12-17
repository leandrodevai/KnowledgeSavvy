"""
KnowledgeSavvy - Document Ingestion Module

This module handles the complete document processing pipeline from upload
to vectorization. It supports multiple file formats, web scraping, and
provides configurable chunking with overlap for optimal vector search.

The module includes:
- Multi-format document loading (PDF, TXT, DOCX, MD, CSV)
- Intelligent text chunking with configurable parameters
- Web scraping capabilities for URL processing
- Vector store integration and indexing
- Database management for document tracking
"""

import logging
import os
from io import StringIO
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    CSVLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredFileLoader,
)
from langchain_core.documents import Document
from streamlit.runtime.uploaded_file_manager import UploadedFile

from ai_models.mdl_factory import EmbeddingModelFactory
from config import settings
from core.vector_store.config import VectorStoreConfig
from core.vector_store.vs_manager import VectorStoreManager
from database import crud

logger = logging.getLogger(__name__)

# Default vector store backend
BACKEND = settings.vector_store_backend


class DocumentProcessor:
    """
    Main class for processing and loading documents from various sources.

    This class handles the conversion of uploaded files into LangChain
    Document objects, supporting multiple file formats and providing
    fallback mechanisms for different processing methods.
    """

    def __init__(self):
        """Initialize the document processor."""
        pass

    def load_document(self, uploaded_file: UploadedFile) -> List[Document]:
        """
        Load a document from a Streamlit UploadedFile.

        This method processes different file types and converts them into
        LangChain Document objects with appropriate metadata. It handles
        text files directly and uses specialized processors for binary formats.

        Args:
            uploaded_file: Streamlit UploadedFile (inherits from BytesIO)

        Returns:
            List[Document]: List of processed documents with metadata
        """
        ext = os.path.splitext(uploaded_file.name)[1].lower()

        # Plain text files - direct processing from memory
        if ext in [".txt", ".md", ".csv"]:
            try:
                content = uploaded_file.read().decode("utf-8")
                uploaded_file.seek(0)  # Reset file pointer for future use

                return [
                    Document(
                        page_content=content,
                        metadata={
                            "source": uploaded_file.name,
                            "file_type": ext[1:],
                            "size": uploaded_file.size,
                        },
                    )
                ]
            except UnicodeDecodeError:
                # If UTF-8 decoding fails, try with ignored errors
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8", errors="ignore")
                uploaded_file.seek(0)

                return [
                    Document(
                        page_content=content,
                        metadata={
                            "source": uploaded_file.name,
                            "file_type": ext[1:],
                            "size": uploaded_file.size,
                            "encoding_issues": True,
                        },
                    )
                ]

        # For PDFs and other binary files
        else:
            try:
                # Try using PyPDFLoader if it's a PDF
                if ext == ".pdf":
                    try:
                        from pypdf import PdfReader

                        uploaded_file.seek(0)
                        reader = PdfReader(uploaded_file)

                        documents = []
                        for i, page in enumerate(reader.pages):
                            text = page.extract_text()
                            if text.strip():  # Only add pages with content
                                documents.append(
                                    Document(
                                        page_content=text,
                                        metadata={
                                            "source": uploaded_file.name,
                                            "page": i + 1,
                                            "file_type": "pdf",
                                            "size": uploaded_file.size,
                                        },
                                    )
                                )

                        uploaded_file.seek(0)  # Reset file pointer
                        return (
                            documents
                            if documents
                            else [
                                Document(
                                    page_content="PDF file processed but no text content found",
                                    metadata={
                                        "source": uploaded_file.name,
                                        "file_type": "pdf",
                                    },
                                )
                            ]
                        )

                    except Exception as pdf_error:
                        logger.warning(
                            f"PyPDF processing failed for {uploaded_file.name}: {pdf_error}"
                        )

                # Fallback: use unstructured if available
                try:
                    from unstructured.partition.auto import partition

                    uploaded_file.seek(0)

                    elements = partition(
                        file=uploaded_file, file_filename=uploaded_file.name
                    )

                    documents = []
                    for element in elements:
                        if str(element).strip():  # Only elements with content
                            documents.append(
                                Document(
                                    page_content=str(element),
                                    metadata={
                                        "source": uploaded_file.name,
                                        "element_type": type(element).__name__,
                                        "file_type": ext[1:],
                                        "size": uploaded_file.size,
                                    },
                                )
                            )

                    uploaded_file.seek(0)
                    return (
                        documents
                        if documents
                        else [
                            Document(
                                page_content="File processed but no content extracted",
                                metadata={
                                    "source": uploaded_file.name,
                                    "file_type": ext[1:],
                                },
                            )
                        ]
                    )

                except ImportError:
                    logger.warning("Unstructured not available for file processing")
                except Exception as unstructured_error:
                    logger.warning(
                        f"Unstructured processing failed: {unstructured_error}"
                    )

                # Last fallback: try to read as text
                uploaded_file.seek(0)
                content = uploaded_file.read().decode("utf-8", errors="ignore")
                uploaded_file.seek(0)

                return [
                    Document(
                        page_content=content,
                        metadata={
                            "source": uploaded_file.name,
                            "file_type": ext[1:],
                            "size": uploaded_file.size,
                            "processed_as": "text_fallback",
                        },
                    )
                ]

            except Exception as e:
                logger.error(
                    f"All processing methods failed for {uploaded_file.name}: {e}"
                )
                return [
                    Document(
                        page_content=f"Error processing file: {uploaded_file.name}",
                        metadata={
                            "source": uploaded_file.name,
                            "error": str(e),
                            "file_type": ext[1:] if ext else "unknown",
                        },
                    )
                ]


def index_documents(
    collection_name: str,
    documents: list[Document],
    chunk_size: int,
    chunk_overlap: int,
    name: str,
    type: str,
) -> int:
    """
    Index documents into the vector store and update the database.

    This function processes documents through the complete pipeline:
    1. Splits documents into chunks with configurable size and overlap
    2. Creates embeddings for each chunk
    3. Stores vectors in the configured vector store
    4. Updates the database with document metadata and chunk IDs

    Args:
        collection_name: Name of the collection to store documents in
        documents: List of LangChain Document objects to process
        chunk_size: Size of each text chunk in characters
        chunk_overlap: Overlap between consecutive chunks
        name: Name/identifier for the document source
        type: Type/category of the document

    Returns:
        int: Number of chunks successfully indexed
    """
    # Create text splitter with specified parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    # Split documents into chunks
    splitted_docs = text_splitter.split_documents(documents)
    logger.info(
        f"Split {len(documents)} documents into {len(splitted_docs)} chunks of size {chunk_size} with overlap {chunk_overlap}"
    )

    # Calculate total tokens for batch sizing
    total_tokens = sum(len(doc.page_content) for doc in splitted_docs)
    logger.debug(f"Total tokens in split documents: {total_tokens}")

    # Determine batch size based on token count
    batch_size = total_tokens // 100000
    if batch_size == 0:
        batch_size = 1
    logger.debug(
        f"Batch size for vector store: {batch_size} (based on total tokens: {total_tokens})"
    )

    # Create batches for processing
    batches = [
        splitted_docs[i : i + batch_size]
        for i in range(0, len(splitted_docs), batch_size)
    ]

    # Create the embedding model
    embeddings = EmbeddingModelFactory().create_embedding_model()

    # Configure and initialize the vector store manager
    config = VectorStoreConfig(
        backend=BACKEND,
        collection_name=collection_name,
    )
    vs_manager = VectorStoreManager(config, embeddings)

    # Add documents to the vector store
    ids = []

    for batch in batches:
        try:
            ids.extend(vs_manager.add_documents(batch))
        except Exception as e:
            logger.error(f"Error adding batch {batch}: - {e}")

    # Update database with source information
    if ids:
        crud.create_source_and_add_to_collection(
            title=name, type=type, collection_name=collection_name, ids=ids
        )
    else:
        logger.warning("No document IDs were generated; skipping database update.")

    logger.info(
        f"Indexed {len(documents)} documents into collection '{collection_name}'"
    )
    return len(ids)


def process_url(
    url: str, collection_name: str, depth: int, chunk_size: int, chunk_overlap: int
) -> int:
    """
    Process a URL by crawling it and adding the content to the specified collection.

    This function uses Tavily's web crawling capabilities to extract content
    from web pages and process it through the same pipeline as uploaded documents.

    Args:
        url: The URL to process and crawl
        depth: The depth of crawling (how many levels deep to go)
        collection_name: The name of the collection to add the content to
        chunk_size: Size of each text chunk in characters
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        int: Number of chunks successfully processed and indexed
    """
    logger.info(
        f"Processing URL: {url} with depth {depth} for collection '{collection_name}'"
    )

    from langchain_tavily import TavilyCrawl

    tavily_crawl = TavilyCrawl()
    try:
        # Invoke the TavilyCrawl to crawl the URL
        res = tavily_crawl.invoke(
            {
                "url": url,
                "max_depth": depth,
                "extract_depth": "advanced",
            }
        )

        if len(res.get("results")) > 0:
            logger.info(
                f"Successfully scraped {url}. Adding content to collection '{collection_name}'"
            )

            # Convert web content to Document objects
            all_docs = [
                Document(
                    page_content=result["raw_content"],
                    metadata={"source": result["url"]},
                )
                for result in res["results"]
            ]
            logger.info(f"Crawled {len(all_docs)} documents from {url}")

            # Process the crawled content through the indexing pipeline
            num_chunks = index_documents(
                collection_name=collection_name,
                documents=all_docs,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                name=url,
                type="webpage",
            )
            return num_chunks
        else:
            logger.error(f"Failed to crawl {url}: {res.get('error', 'Unknown error')}")

    except Exception as e:
        logger.error(f"An error occurred while processing URL {url}: {e}")


def process_documents(
    file: UploadedFile, collection_name: str, chunk_size: int, chunk_overlap: int
) -> int:
    """
    Process documents from a Streamlit UploadedFile.

    This function is the main entry point for processing uploaded files.
    It handles the complete pipeline from file loading to vectorization.

    Args:
        file: Streamlit UploadedFile to process
        collection_name: Name of the collection to store documents in
        chunk_size: Size of each text chunk in characters
        chunk_overlap: Overlap between consecutive chunks

    Returns:
        int: Number of chunks successfully processed and indexed
    """
    document_loader = DocumentProcessor()
    try:
        # Load and process the document
        docs = document_loader.load_document(file)
        logger.info(f"Loaded {len(docs)} documents from file {file.name}")

        # Determine the file type
        file_type = os.path.splitext(file.name)[1].lower().replace(".", "")

        # Process through the indexing pipeline
        num_chunks = index_documents(
            collection_name=collection_name,
            documents=docs,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            name=file.name,
            type=file_type,
        )
        return num_chunks
    except Exception as e:
        logger.error(f"Error processing document {file.name}: {e}")
        return 0
