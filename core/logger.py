"""
KnowledgeSavvy - Logging Configuration Module

This module provides comprehensive logging configuration for the KnowledgeSavvy system.
It sets up both file and console logging with configurable levels, formats,
and rotation policies. The module supports JSON logging for structured output
and colored console output for development environments.

Features:
- Dynamic log level configuration via environment variables
- File logging with rotation and size limits
- JSON structured logging for production environments
- Colored console output for development
- Fallback mechanisms for missing dependencies


"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path

from config import settings


def setup_logging():
    """
    Configure logging dynamically based on environment variables.

    This function sets up a comprehensive logging system with:
    1. File logging with rotation and size limits
    2. Console logging with optional colors
    3. Configurable log levels via DEBUG environment variable
    4. JSON structured logging when available
    5. Fallback mechanisms for missing dependencies

    The function reads configuration from environment variables:
    - DEBUG: If "true", enables debug level logging
    - Default log level is INFO unless DEBUG is enabled

    Log files are stored in data/logs/ with automatic rotation at 10MB
    and retention of 5 backup files.
    """
    # Read configuration from environment
    is_debug = settings.debug
    log_level = logging.DEBUG if is_debug else logging.INFO

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 1. File handler with rotation
    log_file = "data/logs/KnowledgeSavvy.log"
    os.makedirs("data/logs", exist_ok=True)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,  # Keep 5 files: app.log.1, app.log.2, etc.
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)

    # JSON formatter for file logging
    try:
        from pythonjsonlogger import json

        json_formatter = json.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s",
            rename_fields={"levelname": "severity", "asctime": "timestamp"},
        )
        file_handler.setFormatter(json_formatter)
    except ImportError:
        # Fallback if python-json-logger is not installed
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(pathname)s:%(lineno)d]",
            rename_fields={"levelname": "severity", "asctime": "timestamp"},
        )
        file_handler.setFormatter(file_formatter)
        logging.warning("python-json-logger not installed, using text format")

    # 2. Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    try:
        from colorlog import ColoredFormatter

        color_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red,bg_white",
            },
        )
        console_handler.setFormatter(color_formatter)
    except ImportError:
        # Fallback if colorlog is not installed
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        logging.warning("colorlog not installed, using format without colors")

    # Add handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Configure SQLAlchemy logger to use our handlers
    # In debug mode: show INFO level (queries), in production: only WARNING+
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_logger.setLevel(log_level)  # DEBUG or INFO depending on mode
    sqlalchemy_logger.propagate = True  # Use root logger handlers


# Auto-configure logging when module is imported
setup_logging()
