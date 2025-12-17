"""
KnowledgeSavvy - Web Search Node Module

This module contains the web_search node for the RAG workflow. This node
is responsible for performing web searches when the retrieved documents
are insufficient to answer the user's question. It uses Tavily search
to find relevant web content and integrates it with existing documents.
"""

import logging
from typing import Any, Dict

from langchain.schema import Document
from langchain_tavily import TavilySearch

from ai_agent.state import GraphState

logger = logging.getLogger(__name__)

# Initialize Tavily search tool with limited results for quality
web_search_tool = TavilySearch(max_results=3)


def web_search(state: GraphState) -> Dict[str, Any]:
    """
    Perform web search to enhance response quality when documents are insufficient.

    This node enhances the RAG workflow by:
    1. Taking the user's question and existing documents (if any)
    2. Performing a targeted web search using Tavily
    3. Converting web results into Document objects with metadata
    4. Integrating web content with existing documents
    5. Adding relevance scores and source information to web results

    Args:
        state (GraphState): Current workflow state containing:
            - question: User's question for web search
            - documents: Existing documents (may be None if first-time web search)

    Returns:
        Dict[str, Any]: Updated state containing:
            - documents: Combined existing and web search documents
            - question: Original user question
    """
    logger.info("---WEB SEARCH---")
    question = state["question"]

    # Handle case where documents might not exist (first-time web search route)
    if "documents" in state:
        documents = state["documents"]
    else:
        documents = None

    # Perform web search using Tavily
    tavily_results = web_search_tool.invoke({"query": question})["results"]

    # Process each web search result
    for tavily_result in tavily_results:
        # Create metadata with source information and relevance score
        metadata = {
            "source": tavily_result["title"] + "\n" + tavily_result["url"],
            "relevance_score": tavily_result["score"],
        }

        # Create Document object from web content
        web_result = Document(page_content=tavily_result["content"], metadata=metadata)

        # Integrate with existing documents or create new list
        if documents is not None:
            documents.append(web_result)
        else:
            documents = [web_result]

    return {"documents": documents, "question": question}


if __name__ == "__main__":
    # Test the web search functionality
    web_search(state={"question": "agent memory", "documents": None})
