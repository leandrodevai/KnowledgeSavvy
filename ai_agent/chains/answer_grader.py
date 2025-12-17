"""
KnowledgeSavvy - Answer Grader Chain Module

This module defines the answer grader chain used to assess whether generated
answers actually address and resolve the user's original question. It provides
binary scoring to ensure answer quality and relevance.

This grader is part of the multi-stage validation pipeline that helps prevent
hallucinations and ensures generated responses are useful to users.


"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from pydantic import BaseModel, Field

from ai_models import LlmModelFactory


class GradeAnswer(BaseModel):
    """
    Structured output model for answer quality grading.

    This model provides binary scoring to determine if a generated answer
    actually addresses and resolves the user's question.

    Attributes:
        binary_score (bool): Binary score indicating if answer resolves the question
    """

    binary_score: bool = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


# Initialize the LLM model for answer grounding assessment
llm = LlmModelFactory().create_answer_grounding_model()

# Create structured LLM output for answer grading
structured_llm_grader = llm.with_structured_output(GradeAnswer)

# System prompt for the answer quality grader
system = """You are a grader assessing whether an answer addresses / resolves a question \n 
     Give a binary score 'yes' or 'no'. 'Yes' means that the answer resolves the question."""

# Create the answer grading prompt template
answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
    ]
)

# Build the answer grader chain
answer_grader: RunnableSequence = answer_prompt | structured_llm_grader
