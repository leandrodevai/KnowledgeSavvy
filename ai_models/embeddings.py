"""
KnowledgeSavvy - Embedding Models Module

Provider-agnostic wrapper for embedding models (Cohere, Google, etc.).
Handles API key injection and provides unified interface.
"""

from typing import List

from langchain_cohere import CohereEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings

from .base import BaseModel
from .config import ModelProvider


class EmbeddingModel(BaseModel):
    """Wrapper for embedding models with automatic API key injection"""

    def _initialize_client(self):
        """Initialize provider-specific embedding client with API keys"""
        if self.provider == ModelProvider.COHERE:
            # Cohere embeddings with API key from settings
            params = dict(self.params)
            if settings.cohere_api_key:
                params["cohere_api_key"] = settings.cohere_api_key
            return CohereEmbeddings(model=self.model_name, **params)

        elif self.provider == ModelProvider.GOOGLE:
            # Google embeddings with API key from settings
            params = dict(self.params)
            if settings.google_api_key:
                params["google_api_key"] = settings.google_api_key
            return GoogleGenerativeAIEmbeddings(model=self.model_name, **params)

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents"""
        return self.client.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query"""
        return self.client.embed_query(text)

    def __getattr__(self, name):
        """Delegate undefined methods to the underlying client"""
        return getattr(self.client, name)
