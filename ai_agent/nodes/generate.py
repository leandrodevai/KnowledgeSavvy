"""
KnowledgeSavvy - Generate Node Module

This module contains the generate node for the RAG workflow. The generate node
is responsible for creating answers based on retrieved documents and user questions.
It uses a specialized generation chain to ensure high-quality, context-aware responses.
"""

import logging
from typing import Any, Dict

from ai_agent.chains.generation import generation_chain
from ai_agent.state import GraphState

logger = logging.getLogger(__name__)


def generate(state: GraphState) -> Dict[str, Any]:
    """
    Generate an answer based on retrieved documents, user question, and chat history.

    This node is a core component of the RAG workflow that:
    1. Takes the user's question, retrieved documents, and chat history
    2. Uses a specialized generation chain to create context-aware answers
    3. Ensures the response is grounded in the provided documents
    4. Maintains conversation continuity using chat history
    5. Returns the generated answer along with the original context

    Args:
        state (GraphState): Current workflow state containing:
            - question: User's original question
            - documents: Retrieved and graded documents
            - chat_history: Previous conversation context (role/content format)

    Returns:
        Dict[str, Any]: Updated state containing:
            - documents: Original retrieved documents
            - question: Original user question
            - generation: Newly generated answer
    """
    logger.info("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    chat_history = state.get("chat_history", [])

    # Format chat history for the prompt (role/content format)
    formatted_history = ""
    if chat_history:
        history_items = []
        for entry in chat_history[-6:]:  # Use last 6 messages to avoid token limit
            if isinstance(entry, dict):
                role = entry.get("role", "")
                content = entry.get("content", "")
                if role and content:
                    if role == "user":
                        history_items.append(f"User: {content}")
                    elif role == "assistant":
                        history_items.append(f"Assistant: {content}")
        formatted_history = (
            "\n".join(history_items) if history_items else "No previous conversation."
        )
    else:
        formatted_history = "No previous conversation."

    # Generate answer using the specialized generation chain with chat history
    generation = generation_chain.invoke(
        {"context": documents, "question": question, "chat_history": formatted_history}
    )

    # Return updated state with the generated answer
    return {"documents": documents, "question": question, "generation": generation}
