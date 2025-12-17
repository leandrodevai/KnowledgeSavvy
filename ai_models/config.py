"""
KnowledgeSavvy - AI Model Configuration Module

This module defines the configuration structure for AI models used throughout
the KnowledgeSavvy system. It provides enums for model providers, types,
and specific model names, along with a configuration class that manages
model parameters and settings.

The configuration supports multiple AI providers (Google, Cohere) and
different model types for various tasks in the RAG pipeline.


"""

import os
from enum import Enum
from typing import Any, Dict, Optional

from pydantic_settings import BaseSettings


class ModelProvider(str, Enum):
    """
    Enumeration of supported AI model providers.

    This enum defines the available AI service providers that can be used
    for different types of models in the system.
    """

    COHERE = "cohere"
    GOOGLE = "google"


class ModelType(str, Enum):
    """
    Enumeration of model types used in the RAG pipeline.

    Each model type serves a specific purpose in the system:
    - EMBEDDING: For document vectorization and similarity search
    - GENERATOR: For answer generation based on context
    - DOCUMENT_GRADING: For assessing document relevance
    - ANSWER_GROUNDING: For detecting hallucinations and validating answers
    """

    EMBEDDING = "embedding"
    GENERATOR = "generator"
    DOCUMENT_GRADING = "document_grading"
    ANSWER_GROUNDING = "answer_grounding"


class GoogleModels(str, Enum):
    """
    Enumeration of available Google Gemini models.

    These models are available through Google's AI services and provide
    different capabilities and performance characteristics.
    """

    EMBEDDING = "gemini-embedding-001"
    LIGHT = "gemini-2.5-flash-lite"
    MILD = "gemini-2.5-flash"
    PRO = "gemini-2.5-pro"


class CohereModels(str, Enum):
    """
    Enumeration of available Cohere models.

    These models are available through Cohere's AI services and provide
    different capabilities for various tasks in the RAG pipeline.
    """

    EMBEDDING = "embed-v4.0"
    LIGHT = "command-r"
    MILD = "command-r-plus"
    PRO = "command-a-03-2025"


class ModelConfig(BaseSettings):
    """
    Configuration class for AI models used in the KnowledgeSavvy system.

    This class manages the configuration for different model types,
    providers, and their parameters. It provides a centralized way to
    configure all AI models used throughout the application.

    Attributes:
        default_provider (ModelProvider): Default provider for models
        models (Dict): Configuration for each model type with provider, name, and params
    """

    # Global default configuration
    default_provider: ModelProvider = ModelProvider.GOOGLE

    # Specific configuration for each model type
    models: Dict[ModelType, Dict[str, Any]] = {
        ModelType.EMBEDDING: {
            "provider": ModelProvider.COHERE,
            "model_name": CohereModels.EMBEDDING,
            "params": {"max_retries": 10},
        },
        # Alternative embedding configuration (commented out)
        # ModelType.EMBEDDING: {
        #     "provider": ModelProvider.GOOGLE,
        #     "model_name": GoogleModels.EMBEDDING,
        #     "params": {"output_dimensionality": 1536}
        # },
        ModelType.GENERATOR: {
            "provider": ModelProvider.COHERE,
            "model_name": CohereModels.PRO,
            "params": {"temperature": 0.3},  # Low temperature for consistent answers
        },
        ModelType.DOCUMENT_GRADING: {
            "provider": ModelProvider.GOOGLE,
            "model_name": GoogleModels.MILD,
            "params": {
                "temperature": 0.1
            },  # Very low temperature for consistent grading
        },
        ModelType.ANSWER_GROUNDING: {
            "provider": ModelProvider.GOOGLE,
            "model_name": GoogleModels.MILD,
            "params": {
                "temperature": 0.0
            },  # Zero temperature for deterministic validation
        },
    }
