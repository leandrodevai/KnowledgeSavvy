"""
KnowledgeSavvy - Database Models Module

This module defines the SQLAlchemy database models for the KnowledgeSavvy system.
It provides the data structure for collections, sources, and document IDs,
establishing the relationships between different entities in the knowledge base.

The models support:
- Collections: Logical groupings of related documents
- Sources: Individual document sources (files, URLs, etc.)
- Document IDs: Vector store identifiers for document chunks


"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Collection(Base):
    """
    Model representing a collection of related documents.

    Collections serve as logical groupings that organize documents by topic,
    project, or any other meaningful categorization. Each collection can
    contain multiple sources and tracks metadata about the documents within.

    Attributes:
        id: Primary key identifier
        name: Unique name for the collection (used in vector store)
        description: Optional description of the collection's purpose
        document_count: Number of document sources in the collection
        chunks_count: Total number of text chunks across all documents
        created_at: Timestamp when the collection was created
        sources: Relationship to Source objects in this collection
    """

    __tablename__ = "collections"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    document_count = Column(Integer, default=0)
    chunks_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    # Relationship to Source objects
    sources = relationship(
        "Source", back_populates="collection", cascade="all, delete-orphan"
    )

    def __repr__(self):
        """String representation of the Collection model."""
        return f"<Collection(name={self.name}, description={self.description}, chunks_count={self.chunks_count}, created_at={self.created_at})>"


class Source(Base):
    """
    Model representing a document source within a collection.

    Sources represent individual documents, files, or URLs that have been
    processed and added to the knowledge base. Each source is associated
    with a collection and contains multiple document chunks.

    Attributes:
        id: Primary key identifier
        title: Name or title of the source (filename, URL, etc.)
        type: Type of the source (pdf, web, docx, txt, etc.)
        uploaded_at: Timestamp when the source was processed
        collection_id: Foreign key to the parent collection
        collection: Relationship to the parent Collection
        ids: Relationship to DocumentsIds objects for this source
    """

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    type = Column(String)  # e.g., 'pdf', 'web', 'docx'
    uploaded_at = Column(DateTime, default=datetime.now)

    # Foreign key to Collection
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=False)

    # Reverse relationship to Collection
    collection = relationship("Collection", back_populates="sources")

    # Relationship to DocumentsIds
    ids = relationship(
        "DocumentsIds", back_populates="source", cascade="all, delete-orphan"
    )

    def __repr__(self):
        """String representation of the Source model."""
        return f"<Source(title={self.title}, type={self.type}, uploaded_at={self.uploaded_at})>"


class DocumentsIds(Base):
    """
    Model representing individual document chunk identifiers.

    This model stores the vector store IDs for each text chunk created
    from document sources. It maintains the relationship between sources
    and their corresponding vector embeddings for retrieval purposes.

    Attributes:
        id: Primary key identifier
        value: Vector store ID for the document chunk
        source_id: Foreign key to the parent source
        source: Relationship to the parent Source
    """

    __tablename__ = "documentsids"

    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    source = relationship("Source", back_populates="ids")

    def __repr__(self):
        """String representation of the DocumentsIds model."""
        return f"<SourceId(value={self.value}, source_id={self.source_id})>"
