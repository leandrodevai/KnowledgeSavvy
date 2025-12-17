"""
KnowledgeSavvy - Retrieval Grader Chain Module

This module defines the retrieval grader chain used to assess the relevance
of retrieved documents to user questions. It uses structured LLM output to
provide binary relevance scores and numerical relevance scores for each document.

The grader helps filter out irrelevant documents to improve answer quality
and determine when web search augmentation is needed.


"""

from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from ai_models import LlmModelFactory

# Initialize the LLM model for document grading
llm = LlmModelFactory().create_document_grading_model()


class GradeDocuments(BaseModel):
    """
    Structured output model for document relevance grading.

    This model provides both binary and numerical relevance assessments
    to help the system make informed decisions about document quality.

    Attributes:
        relevance (bool): Binary relevance score (True if document is relevant)
        relevance_score (float): Numerical relevance score from 0 to 1
    """

    relevance: bool = Field(
        description="Documents are relevant to the question, True or False"
    )
    relevance_score: float = Field(
        description="Relevance score from 0 to 1", ge=0, le=1
    )


# Create structured LLM output for grading
structured_llm_grader = llm.with_structured_output(GradeDocuments)

# System prompt for the relevance grader
system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
    If the document contains keyword(s) or semantic meaning related to the question, grade it as relevant. \n
    Give a boolean score True or False to indicate whether the document is relevant to the question.\n
    In addition, provide a relevance score from 0 to 1, compatible with a score from a web search."""

# Create the grading prompt template
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Retrieved document: \n\n {document} \n\n User question: {question} \n\n Similarity Score: {similarity_score}",
        ),
    ]
)

# Build the retrieval grader chain
retrieval_grader = grade_prompt | structured_llm_grader
