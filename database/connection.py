"""
KnowledgeSavvy - Database Connection Module

This module handles PostgreSQL database connection setup using SQLAlchemy.
It manages connection pooling, engine configuration, and automatic table creation.
"""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from database import models

logger = logging.getLogger(__name__)

# Database engine configuration with connection pooling
logger.info("Initializing database engine with connection pooling")
engine = create_engine(
    settings.resolved_database_url,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    pool_timeout=20,  # Max wait time for connection
    echo=False,  # SQL logging handled by application logger
)

logger.info(f"Database engine created - Backend: {engine.dialect.name}")

# Create all tables based on model definitions
logger.debug("Creating database tables if they don't exist")
models.Base.metadata.create_all(engine)
logger.debug("Database tables initialized successfully")

# Session factory for database operations
Session = sessionmaker(bind=engine)
logger.debug("Session factory configured")
