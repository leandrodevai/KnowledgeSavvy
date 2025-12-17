"""
KnowledgeSavvy - LLM Models Module

Provider-agnostic wrapper for Large Language Models (Cohere, Google, etc.).
Handles API key injection and provides unified chat interface.
"""

from typing import Any, Dict, List

from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI

from config import settings

from .base import BaseModel
from .config import ModelProvider


class LLMModel(BaseModel):
    """Wrapper for chat/LLM models with automatic API key injection"""

    def _initialize_client(self):
        """Initialize provider-specific LLM client with API keys"""
        if self.provider == ModelProvider.COHERE:
            # Cohere chat model with API key from settings
            params = dict(self.params)
            if settings.cohere_api_key:
                params["cohere_api_key"] = settings.cohere_api_key
            return ChatCohere(model=self.model_name, **params)

        elif self.provider == ModelProvider.GOOGLE:
            # Google chat model with API key from settings
            params = dict(self.params)
            if settings.google_api_key:
                params["google_api_key"] = settings.google_api_key
            return ChatGoogleGenerativeAI(model=self.model_name, **params)

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def invoke(self, messages: List[Any]) -> str:
        """Invoke the model with a list of messages"""
        response = self.client.invoke(messages)
        return response.content

    def __getattr__(self, name):
        """Delegate undefined methods to the underlying client"""
        return getattr(self.client, name)
