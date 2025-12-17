"""
KnowledgeSavvy - Chat Interface Module

This module provides the chat interface for interacting with the knowledge base.
It handles user queries, processes them through the RAG agent, and displays
responses with source documents and metadata.


"""

import logging
import os

import streamlit as st

from config import settings

logger = logging.getLogger(__name__)


def chat_interface():
    """
    Main chat interface for querying the knowledge base.

    This function:
    1. Displays the chat interface header
    2. Handles user input and query processing
    3. Processes queries through the RAG agent
    4. Displays responses with source information
    5. Manages chat history and configuration
    """
    st.header("💬 Query Your Knowledge Base")

    if not st.session_state.current_collection:
        st.warning("⚠️ Select or create a collection to get started")
        return

    # Chat configuration
    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("⚙️ Configuration")
        # temperature = st.slider("LLM Temperature:", 0.0, 1.0, 0.7)
        max_docs = st.slider("Max documents:", 1, 10, 3)

        # Toggle to show sources
        show_sources = st.checkbox("Show sources", value=True)

        # Button to clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    with col1:
        # Container for input (always at top)
        input_container = st.container()

        # Container for chat history (below input)
        chat_container = st.container()

        with input_container:
            # Input for new question
            if prompt := st.chat_input("Ask your question..."):
                # Add question to chat
                st.session_state.chat_history.append(
                    {"role": "user", "content": prompt}
                )

                # Process with RAG graph
                with st.spinner("🤔 Processing your query..."):
                    try:
                        from ai_models.mdl_factory import EmbeddingModelFactory
                        from core.vector_store.config import VectorStoreConfig
                        from core.vector_store.vs_manager import VectorStoreManager

                        config = VectorStoreConfig(
                            backend=settings.vector_store_backend,
                            collection_name=st.session_state.current_collection,
                        )
                        vs_manager = VectorStoreManager(
                            config, EmbeddingModelFactory().create_embedding_model()
                        )

                        result = st.session_state.agent.invoke(
                            input={
                                "question": prompt,
                                "retriever": vs_manager.as_retriever(
                                    search_kwargs={"k": max_docs}
                                ),
                                "chat_history": st.session_state.chat_history[:-1],
                            }
                        )

                        # Add response to history BEFORE displaying
                        st.session_state.chat_history.append(
                            {
                                "role": "assistant",
                                "content": result["generation"],
                                "metadata": {
                                    "used_web_search": result.get(
                                        "used_web_search", False
                                    ),
                                    "source_docs": result.get("documents", []),
                                },
                            }
                        )

                        # Force reload to show new response
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error processing query: {e}")

        with chat_container:
            # Display chat history (most recent first)
            for message in reversed(st.session_state.chat_history):
                with st.chat_message(message["role"]):
                    st.write(message["content"])

                    # Show metadata if it's an assistant response
                    if message["role"] == "assistant" and show_sources:
                        if "metadata" in message:
                            with st.expander("📚 View sources and details"):
                                metadata = message["metadata"]

                                # Show if web search was used
                                if metadata.get("used_web_search"):
                                    st.info("🌐 Enhanced with web search")

                                # Show source documents
                                if "source_docs" in metadata:
                                    if metadata["used_web_search"]:
                                        st.write("🌐 Enhanced with web search.")
                                    st.write("**Source documents:**")
                                    for i, doc in enumerate(metadata["source_docs"], 1):
                                        if "similarity_score" in doc.metadata:
                                            relevance_score = doc.metadata.get(
                                                "relevance_score", "Unknown"
                                            )
                                            similarity_score = doc.metadata.get(
                                                "similarity_score", "unknown"
                                            )
                                            source = doc.metadata.get(
                                                "source", "Unknown source"
                                            )
                                            st.write(
                                                f"{i}. {source} (Relevance Score: {relevance_score}, Similarity Score: {similarity_score})"
                                            )
                                        else:
                                            relevance_score = doc.metadata.get(
                                                "relevance_score", "Unknown"
                                            )
                                            source = doc.metadata.get(
                                                "source", "Unknown source"
                                            )
                                            st.write(
                                                f"{i}. {source} (Relevance Score: {relevance_score})"
                                            )
