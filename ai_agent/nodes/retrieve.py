"""
KnowledgeSavvy - Retrieve Node Module

This module contains the retrieve node for the RAG workflow. The retrieve node
is responsible for finding relevant documents from the vector store based on
the user's question. It handles different vector store backends and provides
similarity scores for document relevance assessment.
"""

import logging
from typing import Any, Dict

from ai_agent.state import GraphState

logger = logging.getLogger(__name__)


def retrieve(state: GraphState) -> Dict[str, Any]:
    """
    Retrieve relevant documents from the vector store based on user question.

    This node is the entry point of the RAG workflow that:
    1. Takes the user's question and vector store retriever
    2. Performs similarity search to find relevant documents
    3. Adds similarity scores to document metadata for grading
    4. Handles different vector store backends gracefully
    5. Returns retrieved documents with enhanced metadata

    Args:
        state (GraphState): Current workflow state containing:
            - question: User's question for document retrieval
            - retriever: Vector store retriever instance

    Returns:
        Dict[str, Any]: Updated state containing:
            - documents: Retrieved documents with similarity scores
            - question: Original user question
    """
    logger.info("---RETRIEVE---")
    question = state["question"]
    retriever = state["retriever"]

    # Check if retriever has vectorstore method for similarity_search_with_score
    if hasattr(retriever, "vectorstore"):
        # Get k from search_kwargs or use 4 as default
        k = getattr(retriever, "search_kwargs", {}).get("k", 4)

        # Perform similarity search with scores
        docs_with_scores = retriever.vectorstore.similarity_search_with_score(
            question, k=k
        )

        # Add similarity scores to document metadata
        documents = []
        for doc, score in docs_with_scores:
            doc.metadata["similarity_score"] = float(score)
            documents.append(doc)
    else:
        # Fallback to original method if vectorstore not available
        documents = retriever.invoke(question)

    return {"documents": documents, "question": question}
