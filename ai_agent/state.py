"""
KnowledgeSavvy - Graph State Module

This module defines the state structure used throughout the RAG workflow.
The GraphState TypedDict provides a type-safe way to pass data between
different nodes in the workflow graph.
"""

from typing import List, Optional, TypedDict

from langchain_core.vectorstores import VectorStoreRetriever


class GraphState(TypedDict):
    """
    Represents the state of the RAG workflow graph.

    This TypedDict defines the data structure that flows through the entire
    workflow, ensuring type safety and clear data contracts between nodes.
    The state maintains conversation context and document information throughout
    the multi-stage RAG pipeline.

    Attributes:
        question (str): The user's original question/query
        generation (str): The LLM-generated answer (initially empty, populated by generate node)
        web_search (bool): Flag indicating whether web search should be performed
                          (True if retrieved documents are insufficient)
        documents (List[str]): List of retrieved and graded documents with metadata
        retriever (Optional[VectorStoreRetriever]): Vector store retriever instance
                                                   for document retrieval operations
        chat_history (List[dict]): Previous conversation context for maintaining continuity.
                                  Each entry contains user and assistant messages.
    """

    question: str
    generation: str
    web_search: bool
    documents: List[str]
    retriever: Optional[VectorStoreRetriever]
    chat_history: List[dict]
