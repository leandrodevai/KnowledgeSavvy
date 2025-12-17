"""
KnowledgeSavvy - Main Application Entry Point

This module serves as the main entry point for the KnowledgeSavvy RAG system.
It provides a Streamlit-based web interface for document management, chat,
and knowledge base operations.
"""

# Import SSL configuration for secure API connections
import config.ssl_config  # Auto-configures SSL on import

# Application imports
import logging
import re
import streamlit as st

# Import and initialize logging
from core.logger import setup_logging

from config import settings

from app.modules.upload import upload_interface
from app.modules.chat import chat_interface
from app.modules.dashboard import dashboard_interface
from app.modules.management import document_management_interface

logger = logging.getLogger(__name__)

# Page configuration (MUST always go first)
st.set_page_config(
    page_title="RAG System - Knowledge Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)



# Internal imports (after config)
# from core.vector_store import VectorStoreManager
from database.crud import create_collection, get_all_collections
from ai_agent.graph import agent


# Initialize session state
if "current_collection" not in st.session_state:
    st.session_state.current_collection = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = agent


def main():
    """
    Main application function that renders the KnowledgeSavvy interface.

    This function:
    1. Displays the main header and description
    2. Renders the sidebar for collection management
    3. Creates the main tab interface for different functionalities
    4. Handles collection creation and selection
    """
    # Main header
    st.title("🧠 RAG Knowledge Assistant")
    st.markdown("*Upload documents, and retrieve specific information from them*")

    # Sidebar for collection selection
    with st.sidebar:
        st.header("📁 Topic Management")

        # Existing collection selector
        collections = get_all_collections()
        collection_names = [col.name for col in collections] if collections else []

        if collection_names:
            selected = st.selectbox(
                "Select Collection:",
                options=["-- New Topic --"] + collection_names,
                key="collection_selector",
            )

            if selected != "-- New Topic --":
                st.session_state.current_collection = selected
                # Show collection stats
                current_col = next(col for col in collections if col.name == selected)
                st.info(f"📊 {current_col.document_count} document(s)")
                st.info(f"📅 Created: {current_col.created_at.strftime('%d/%m/%Y')}")
                st.info(f"📝 {current_col.description or 'No description'}")

        # Create new collection
        st.subheader("➕ New Topic")
        new_collection_name = st.text_input(
            "Collection name:",
            help="Only lowercase letters, numbers, and hyphens. Example: my-topic-2025",
        )
        new_collection_desc = st.text_area("Description (optional):")

        if st.button("Create Collection"):
            if new_collection_name:
                # Validate name format
                if not re.match(r"^[a-z0-9-]+$", new_collection_name):
                    st.error(
                        "❌ Name can only contain lowercase letters, numbers, and hyphens"
                    )
                elif new_collection_name in collection_names:
                    st.error("❌ Collection name already exists")
                elif new_collection_name.startswith(
                    "-"
                ) or new_collection_name.endswith("-"):
                    st.error("❌ Name cannot start or end with a hyphen")
                else:
                    try:
                        create_collection(new_collection_name, new_collection_desc)
                        st.success(f"Collection '{new_collection_name}' created!")
                        st.rerun()  # Refresh to show in selector
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error("Name is required")

    # Main tab interface
    tab1, tab2, tab3, tab4 = st.tabs(
        ["💬 Chat", "📤 Upload Documents", "📊 Dashboard", "🗂️ Manage Documents"]
    )

    with tab1:
        chat_interface()

    with tab2:
        upload_interface()

    with tab3:
        dashboard_interface()

    with tab4:
        document_management_interface()


if __name__ == "__main__":
    main()
