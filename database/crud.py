"""
KnowledgeSavvy - Database CRUD Operations Module

This module provides database operations for collections, sources, and document IDs
with automatic session management, logging, and error handling.

Key features:
- Decorator-based session management with automatic commit/rollback
- Comprehensive logging for all operations
- Type-safe CRUD operations with proper error handling
- Collection and source lifecycle management
"""

import logging
from functools import wraps
from typing import Any, Callable, List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import connection, models

# Setup logger for this module
logger = logging.getLogger(__name__)


def db_operation(operation_name: str, read_only: bool = False):
    """
    Decorator for database operations with automatic session management.

    Provides consistent logging, error handling, and session lifecycle management
    for all database operations. Automatically commits write operations and
    handles rollback on errors.

    Args:
        operation_name: Description of the operation for logging
        read_only: True for read operations (no commit), False for write operations
    """

    def decorator(func: Callable) -> Callable:
        # Create a new function that matches the original signature minus the session parameter
        import inspect

        sig = inspect.signature(func)

        # Remove 'session' parameter from signature
        params = [p for name, p in sig.parameters.items() if name != "session"]
        new_sig = sig.replace(parameters=params)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Log operation start
            logger.info(f"Starting {operation_name}")
            if args or kwargs:
                logger.debug(f"Parameters - args: {args}, kwargs: {kwargs}")

            session = connection.Session()
            try:
                # Execute the function with session as first parameter
                result = func(session, *args, **kwargs)

                # Commit only for write operations
                if not read_only:
                    session.commit()

                logger.info(f"Successfully completed {operation_name}")
                return result

            except IntegrityError as e:
                logger.error(f"Integrity error in {operation_name}: {e}")
                session.rollback()
                raise
            except SQLAlchemyError as e:
                logger.error(f"Database error in {operation_name}: {e}")
                session.rollback()
                raise
            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {e}")
                session.rollback()
                raise
            finally:
                session.close()
                logger.debug(f"Database session closed for {operation_name}")

        # Apply the new signature to the wrapper
        wrapper.__signature__ = new_sig
        return wrapper

    return decorator


@db_operation("get all collections", read_only=True)
def get_all_collections(session) -> List[models.Collection]:
    """Get all collections from database."""
    collections = session.query(models.Collection).all()
    logger.debug(
        f"Retrieved {len(collections)} collections: {[c.name for c in collections]}"
    )
    return collections


@db_operation("create collection")
def create_collection(
    session, name: str, description: Optional[str] = None
) -> models.Collection:
    """Create a new collection with duplicate name validation."""
    logger.debug(f"Creating collection '{name}' with description: '{description}'")

    # Check if collection already exists
    existing = session.query(models.Collection).filter_by(name=name).first()
    if existing:
        logger.warning(f"Collection '{name}' already exists with ID: {existing.id}")
        raise IntegrityError(
            f"Collection with name '{name}' already exists", None, None
        )

    new_collection = models.Collection(name=name, description=description)
    session.add(new_collection)
    session.flush()  # Get ID before commit

    logger.info(f"Created collection '{name}' with ID: {new_collection.id}")
    return new_collection


@db_operation("create source and add to collection")
def create_source_and_add_to_collection(
    session, title: str, type: str, collection_name: str, ids: List[str]
) -> Optional[models.Source]:
    """Create a source and add it to a collection with document IDs."""
    logger.debug(
        f"Creating source '{title}' in collection '{collection_name}' with {len(ids)} IDs"
    )

    # Find the collection
    collection = (
        session.query(models.Collection).filter_by(name=collection_name).first()
    )
    if not collection:
        logger.warning(f"Collection '{collection_name}' not found")
        return None

    # Create the source
    new_source = models.Source(title=title, type=type, collection_id=collection.id)
    session.add(new_source)
    session.flush()  # Get the source ID

    # Update collection counters
    collection.document_count += 1
    collection.chunks_count += len(ids)

    # Create document IDs
    for id_value in ids:
        new_id = models.DocumentsIds(value=id_value, source_id=new_source.id)
        session.add(new_id)

    logger.info(
        f"Created source '{title}' (ID: {new_source.id}) with {len(ids)} document IDs"
    )
    return new_source


@db_operation("delete collection")
def delete_collection(session, collection_name: str) -> None:
    """Delete a collection and all its related data."""
    collection = (
        session.query(models.Collection).filter_by(name=collection_name).first()
    )
    if collection:
        # Get counts before deletion for logging
        sources_count = len(collection.sources)
        total_document_ids = sum(len(source.ids) for source in collection.sources)

        logger.info(
            f"Deleting collection '{collection_name}' (ID: {collection.id}) with "
            f"{sources_count} sources and {total_document_ids} document IDs"
        )

        session.delete(collection)
        logger.info(f"Deleted collection '{collection_name}' and all related data")
    else:
        logger.warning(f"Collection '{collection_name}' not found for deletion")


@db_operation("delete source")
def delete_source(session, source_id: int) -> None:
    """Delete a source and all its related document IDs."""
    source = session.query(models.Source).filter_by(id=source_id).first()
    if source:
        source_title = source.title
        collection_name = source.collection.name if source.collection else "Unknown"
        document_ids_count = len(source.ids)

        logger.info(
            f"Deleting source '{source_title}' (ID: {source_id}) from collection "
            f"'{collection_name}' with {document_ids_count} document IDs"
        )

        # Update collection counters before deletion
        if source.collection:
            source.collection.document_count -= 1

        session.delete(source)
        logger.info(
            f"Deleted source '{source_title}' and {document_ids_count} related document IDs"
        )
    else:
        logger.warning(f"Source with ID {source_id} not found for deletion")


@db_operation("get all sources in collection", read_only=True)
def get_all_source_in_collection(session, collection_name: str) -> List[models.Source]:
    """Get all sources in a collection."""
    collection = (
        session.query(models.Collection).filter_by(name=collection_name).first()
    )
    if collection:
        sources = collection.sources
        logger.info(f"Found {len(sources)} sources in collection '{collection_name}'")
        logger.debug(f"Source titles: {[s.title for s in sources]}")
        return sources
    else:
        logger.warning(f"Collection '{collection_name}' not found")
        return []


@db_operation("get all document IDs in source", read_only=True)
def get_all_ids_in_source(session, source_id: int) -> List[models.DocumentsIds]:
    """Get all document IDs in a source."""
    source = session.query(models.Source).filter_by(id=source_id).first()
    if source:
        ids = source.ids
        logger.info(
            f"Found {len(ids)} document IDs in source '{source.title}' (ID: {source_id})"
        )
        logger.debug(f"Document ID values: {[doc_id.value for doc_id in ids]}")
        return ids
    else:
        logger.warning(f"Source with ID {source_id} not found")
        return []
