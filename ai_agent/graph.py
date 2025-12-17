"""
KnowledgeSavvy - AI Agent Graph Module

This module defines the core RAG workflow using LangGraph. It implements
a multi-stage validation pipeline that includes document retrieval,
relevance grading, answer generation, and hallucination detection.

The workflow ensures high-quality responses by:
1. Retrieving relevant documents
2. Grading document relevance
3. Generating answers with context
4. Validating answer quality and grounding
"""

import logging

from langgraph.graph import END, StateGraph

from ai_agent.chains.answer_grader import answer_grader
from ai_agent.chains.hallucination_grader import hallucination_grader
from ai_agent.nodes import generate, grade_documents, retrieve, web_search
from ai_agent.state import GraphState

from .consts import GENERATE, GRADE_DOCUMENTS, RETRIEVE, WEBSEARCH

logger = logging.getLogger(__name__)


def decide_to_generate(state):
    """
    Decision function that determines whether to generate an answer or perform web search.

    This function evaluates the state after document grading and decides the next step:
    - If web_search flag is True: Documents were insufficient, perform web search
    - If web_search flag is False: Sufficient relevant documents, generate answer

    Args:
        state (GraphState): Current graph state containing documents and flags

    Returns:
        str: Next node to execute (WEBSEARCH or GENERATE)
    """
    logger.info("---ASSESS GRADED DOCUMENTS---")

    if state["web_search"]:
        logger.info(
            "---DECISION: NOT ALL DOCUMENTS ARE RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
        )
        return WEBSEARCH
    else:
        logger.info("---DECISION: GENERATE---")
        return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    """
    Multi-stage validation function that grades the generated answer.

    This function performs two critical validations:
    1. Hallucination Detection: Ensures the answer is grounded in retrieved documents
    2. Answer Quality: Verifies the answer actually addresses the user's question

    Args:
        state (GraphState): Current graph state containing question, documents, and generation

    Returns:
        str: Validation result indicating next action:
            - "useful": Answer is valid and addresses the question
            - "not useful": Answer doesn't address the question
            - "not supported": Answer contains hallucinations
    """
    logger.info("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    # First validation: Check if generation is grounded in documents
    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if hallucination_grade := score.binary_score:
        logger.info("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        logger.info("---GRADE GENERATION vs QUESTION---")

        # Second validation: Check if answer addresses the question
        score = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            logger.info("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            logger.info("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        logger.info("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


# Initialize the workflow graph
workflow = StateGraph(GraphState)

# Add nodes to the workflow
workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)

# Set the entry point
workflow.set_entry_point(RETRIEVE)

# Define the main workflow path
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)

# Conditional branching after document grading
workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)

# Conditional branching after answer generation for quality validation
workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,  # Retry generation if hallucination detected
        "useful": END,  # End if answer is valid
        "not useful": WEBSEARCH,  # Use web search if answer doesn't address question
    },
)

# Web search always leads to generation
workflow.add_edge(WEBSEARCH, GENERATE)

# Final generation step always leads to end
workflow.add_edge(GENERATE, END)

# Compile the workflow into an executable agent
agent = workflow.compile()

# Generate a visual representation of the workflow
agent.get_graph().draw_mermaid_png(output_file_path="RAG_pipeline.png")
