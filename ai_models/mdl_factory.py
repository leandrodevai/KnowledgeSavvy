"""
KnowledgeSavvy - AI Model Factory Module

This module provides factory classes for creating different types of AI models
used throughout the KnowledgeSavvy system. It supports multiple providers
(Google, Cohere) and model types (embeddings, generators, graders) with
configurable parameters and fallback mechanisms.

The factories ensure consistent model creation and configuration across
the entire application while providing flexibility for different use cases.


"""

import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel

from .config import ModelConfig, ModelProvider, ModelType
from .embeddings import EmbeddingModel
from .llms import LLMModel

logger = logging.getLogger(__name__)


class EmbeddingModelFactory:
    """
    Factory class for creating embedding models based on configuration.

    This factory creates embedding models used for document vectorization
    and similarity search. It supports multiple providers and model types
    with configurable parameters.

    Attributes:
        config (ModelConfig): Configuration object containing model settings
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize the embedding model factory.

        Args:
            config (ModelConfig, optional): Configuration object. Uses default if None.
        """
        self.config = config or ModelConfig()
        logger.info("EmbeddingModelFactory initialized")

    def create_embedding_model(
        self,
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
        **kwargs,
    ) -> EmbeddingModel:
        """
        Create an embedding model instance.

        Args:
            provider (ModelProvider, optional): Specific provider to use
            model_name (str, optional): Specific model name to use
            **kwargs: Additional parameters to override configuration

        Returns:
            EmbeddingModel: Configured embedding model client

        Raises:
            Exception: If model creation fails
        """
        try:
            model_config = self.config.models[ModelType.EMBEDDING]

            # Use provided parameters or fall back to configuration defaults
            provider = provider or model_config["provider"]
            model_name = model_name or model_config["model_name"]
            params = {**model_config["params"], **kwargs}

            logger.debug(
                f"Creating embedding model: {provider.value}/{model_name} with params {params}"
            )

            # Create the embedding model instance
            embedding_model = EmbeddingModel(
                provider=provider, model_name=model_name, params=params
            )

            logger.info(
                f"Embedding model created successfully: {provider.value}/{model_name} with params {params}"
            )
            return embedding_model.client

        except Exception as e:
            logger.error(f"Error creating embedding model: {str(e)}")
            raise


class LlmModelFactory:
    """
    Factory class for creating chat/LLM models based on configuration.

    This factory creates different types of LLM models used for various
    tasks in the RAG pipeline: answer generation, document grading,
    and hallucination detection.

    Attributes:
        config (ModelConfig): Configuration object containing model settings
    """

    def __init__(self, config: Optional[ModelConfig] = None):
        """
        Initialize the LLM model factory.

        Args:
            config (ModelConfig, optional): Configuration object. Uses default if None.
        """
        self.config = config or ModelConfig()
        logger.info("LlmModelFactory initialized")

    def create_generator_model(
        self,
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
        **kwargs,
    ) -> BaseChatModel:
        """
        Create the main answer generation model.

        This model is used for generating responses to user questions
        based on retrieved documents and context.

        Args:
            provider (ModelProvider, optional): Specific provider to use
            model_name (str, optional): Specific model name to use
            **kwargs: Additional parameters to override configuration

        Returns:
            BaseChatModel: Configured chat model for answer generation

        Raises:
            Exception: If model creation fails
        """
        try:
            model_config = self.config.models[ModelType.GENERATOR]

            # Use provided parameters or fall back to configuration defaults
            provider = provider or model_config["provider"]
            model_name = model_name or model_config["model_name"]
            params = {**model_config["params"], **kwargs}

            logger.debug(
                f"Creating generator model: {provider.value}/{model_name} with params {params}"
            )

            # Create the LLM model instance
            llm_model = LLMModel(
                provider=provider, model_name=model_name, params=params
            )

            logger.info(
                f"Generator model created successfully: {provider.value}/{model_name} with params {params}"
            )
            return llm_model.client

        except Exception as e:
            logger.error(f"Error creating generator model: {str(e)}")
            raise

    def create_document_grading_model(
        self,
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
        **kwargs,
    ) -> BaseChatModel:
        """
        Create the document relevance grading model.

        This model is used for assessing whether retrieved documents
        are relevant to user questions, helping filter out irrelevant content.

        Args:
            provider (ModelProvider, optional): Specific provider to use
            model_name (str, optional): Specific model name to use
            **kwargs: Additional parameters to override configuration

        Returns:
            BaseChatModel: Configured chat model for document grading

        Raises:
            Exception: If model creation fails
        """
        try:
            model_config = self.config.models[ModelType.DOCUMENT_GRADING]

            # Use provided parameters or fall back to configuration defaults
            provider = provider or model_config["provider"]
            model_name = model_name or model_config["model_name"]
            params = {**model_config["params"], **kwargs}

            logger.debug(
                f"Creating document grading model: {provider.value}/{model_name} with params {params}"
            )

            # Create the LLM model instance
            llm_model = LLMModel(
                provider=provider, model_name=model_name, params=params
            )

            logger.info(
                f"Document grading model created successfully: {provider.value}/{model_name} with params {params}"
            )
            return llm_model.client

        except Exception as e:
            logger.error(f"Error creating document grading model: {str(e)}")
            raise

    def create_answer_grounding_model(
        self,
        provider: Optional[ModelProvider] = None,
        model_name: Optional[str] = None,
        **kwargs,
    ) -> BaseChatModel:
        """
        Create the hallucination detection model.

        This model is used for validating that generated answers are
        grounded in retrieved documents and don't contain hallucinations.

        Args:
            provider (ModelProvider, optional): Specific provider to use
            model_name (str, optional): Specific model name to use
            **kwargs: Additional parameters to override configuration

        Returns:
            BaseChatModel: Configured chat model for hallucination detection

        Raises:
            Exception: If model creation fails
        """
        try:
            model_config = self.config.models[ModelType.ANSWER_GROUNDING]

            # Use provided parameters or fall back to configuration defaults
            provider = provider or model_config["provider"]
            model_name = model_name or model_config["model_name"]
            params = {**model_config["params"], **kwargs}

            logger.debug(
                f"Creating answer grounding model: {provider.value}/{model_name} with params {params}"
            )

            # Create the LLM model instance
            llm_model = LLMModel(
                provider=provider, model_name=model_name, params=params
            )

            logger.info(
                f"Answer grounding model created successfully: {provider.value}/{model_name} with params {params}"
            )
            return llm_model.client

        except Exception as e:
            logger.error(f"Error creating answer grounding model: {str(e)}")
            raise
