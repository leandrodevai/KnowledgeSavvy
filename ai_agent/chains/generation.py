"""
KnowledgeSavvy - Generation Chain Module

This module defines the generation chain used by the generate node in the RAG workflow.
It creates a specialized prompt template and chain for generating high-quality,
context-aware answers based on retrieved documents, user questions, and chat history.
"""

from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ai_models import LlmModelFactory

# Initialize the LLM model for answer generation
llm = LlmModelFactory().create_generator_model()

# Alternative: Use a pre-built prompt from LangChain Hub
# prompt = hub.pull("rlm/rag-prompt")

# Enhanced prompt template with chat history support for RAG applications
prompt = """
You are an intelligent assistant for question-answering tasks. Your goal is to provide accurate, helpful, and contextual responses.

INSTRUCTIONS:
- Use the retrieved context below to answer the current question
- Consider the chat history to maintain conversation continuity
- IMPORTANT: Always respond in the same language as the current question
- If you don't know the answer, clearly state that you don't know
- Keep answers concise but complete
- Reference specific information from the context when possible
- Maintain a conversational tone that builds on previous interactions

CHAT HISTORY:
{chat_history}

RETRIEVED CONTEXT:
{context}

CURRENT QUESTION: {question}

ANSWER:
"""

# Create the prompt template with chat history support
generation_prompt = ChatPromptTemplate.from_template(prompt)

# Build the generation chain: prompt -> LLM -> string output
generation_chain = generation_prompt | llm | StrOutputParser()
