"""
KnowledgeSavvy - Base Model Module

Abstract base class for all AI models with lazy client initialization.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .config import ModelProvider, ModelType

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Base class for AI models with unified provider interface"""

    def __init__(
        self,
        provider: ModelProvider,
        model_name: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        # Initialize model configuration
        self.provider = provider
        self.model_name = model_name
        self.params = params or {}
        self._client = None  # Lazy-loaded client instance

    @abstractmethod
    def _initialize_client(self):
        """Must be implemented by subclasses to create provider-specific client"""
        pass

    @property
    def client(self):
        """Lazy-loads the client on first access for better performance"""
        if self._client is None:
            self._client = self._initialize_client()
        return self._client
