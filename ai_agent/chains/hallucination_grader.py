"""
KnowledgeSavvy - Hallucination Grader Chain Module

This module defines the hallucination grader chain used to detect whether
generated answers are grounded in and supported by the retrieved documents.
It provides binary scoring to prevent AI hallucinations and ensure factual accuracy.

This grader is a critical component of the multi-stage validation pipeline
that maintains the integrity and reliability of RAG-generated responses.


"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from pydantic import BaseModel, Field

from ai_models import LlmModelFactory

# Initialize the LLM model for hallucination detection
llm = LlmModelFactory().create_answer_grounding_model()


class GradeHallucinations(BaseModel):
    """
    Structured output model for hallucination detection grading.

    This model provides binary scoring to determine if a generated answer
    is grounded in and supported by the provided facts/documents.

    Attributes:
        binary_score (bool): Binary score indicating if answer is grounded in facts
    """

    binary_score: bool = Field(
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )


# Create structured LLM output for hallucination detection
structured_llm_grader = llm.with_structured_output(GradeHallucinations)

# System prompt for the hallucination detector
system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""

# Create the hallucination grading prompt template
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
    ]
)

# Build the hallucination grader chain
hallucination_grader: RunnableSequence = hallucination_prompt | structured_llm_grader
