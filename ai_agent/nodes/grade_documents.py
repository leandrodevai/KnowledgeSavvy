"""
KnowledgeSavvy - Grade Documents Node Module

This module contains the grade_documents node for the RAG workflow. This node
is responsible for assessing the relevance of retrieved documents to the user's
question. It uses AI-powered grading to filter out irrelevant documents and
determines whether web search should be performed to enhance the response.
"""

import logging
from typing import Any, Dict

from ai_agent.chains.retrieval_grader import retrieval_grader
from ai_agent.state import GraphState

logger = logging.getLogger(__name__)


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Assess the relevance of retrieved documents to the user's question.

    This node performs intelligent document filtering by:
    1. Evaluating each retrieved document for relevance to the question
    2. Using AI-powered grading with similarity scores as context
    3. Filtering out irrelevant documents to improve answer quality
    4. Setting a web_search flag if insufficient relevant documents are found
    5. Adding relevance scores to document metadata for transparency

    Args:
        state (GraphState): Current workflow state containing:
            - question: User's original question
            - documents: Retrieved documents with similarity scores

    Returns:
        Dict[str, Any]: Updated state containing:
            - documents: Filtered relevant documents with relevance scores
            - question: Original user question
            - web_search: Boolean flag indicating if web search is needed
    """
    logger.info("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    web_search = False

    # Grade each document for relevance
    for d in documents:
        # Use AI grader with document content, question, and similarity score
        score = retrieval_grader.invoke(
            {
                "question": question,
                "document": d.page_content,
                "similarity_score": d.metadata.get("similarity_score", "unknown"),
            }
        )
        score = score.model_dump()
        grade = score.get("relevance", "no")

        if grade:
            logger.info("---GRADE: DOCUMENT RELEVANT---")
            # Add relevance score to document metadata
            d.metadata["relevance_score"] = score.get("relevance_score", 0.0)
            filtered_docs.append(d)
        else:
            logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
            # Flag for web search if documents are insufficient
            web_search = True
            continue

    return {"documents": filtered_docs, "question": question, "web_search": web_search}
