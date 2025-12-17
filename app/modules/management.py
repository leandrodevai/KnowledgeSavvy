"""
KnowledgeSavvy - Document Management Module

This module provides comprehensive document management capabilities including
viewing, deleting individual sources, and removing entire collections.
It offers a safe interface with multiple confirmation steps for destructive operations.


"""

import logging

import streamlit as st

from database.crud import (
    delete_collection,
    delete_source,
    get_all_collections,
    get_all_source_in_collection,
)

logger = logging.getLogger(__name__)


def document_management_interface():
    """
    Main interface for document and collection management.

    This function:
    1. Displays existing documents and collections
    2. Provides options to delete individual sources
    3. Offers collection deletion with safety confirmations
    4. Shows detailed information about what will be deleted
    5. Implements multiple confirmation steps for safety
    """
    st.header("🗂️ Document Management")
    st.markdown("Here you can manage your uploaded documents.")

    # Viewing section
    st.subheader("📋 Existing Documents")
    collections = get_all_collections()
    for col in collections:
        st.subheader(f"📁 {col.name}")
        st.markdown(f"Created: {col.created_at.strftime('%d/%m/%Y')}")
        st.markdown(f"Description: {col.description or 'No description'}")
        st.markdown("Documents contained:")
        sources = get_all_source_in_collection(col.name)
        if sources:
            for src in sources:
                st.markdown(
                    f" Name: {src.title}, Type: {src.type}, Date: {src.uploaded_at.strftime('%d/%m/%Y')}"
                )
        else:
            st.markdown("No documents in this collection.")

    st.divider()

    # Deletion section
    st.subheader("🗑️ Delete Documents")

    # Tabs to organize deletion options
    tab1, tab2 = st.tabs(["Delete Individual Source", "Delete Complete Collection"])

    with tab1:
        st.markdown("**Delete a specific document:**")

        if collections:
            # Select collection
            collection_names = [col.name for col in collections]
            selected_collection_name = st.selectbox(
                "Select the collection:",
                collection_names,
                key="delete_source_collection",
            )

            # Find the selected collection
            selected_collection = next(
                col for col in collections if col.name == selected_collection_name
            )
            sources = get_all_source_in_collection(selected_collection.name)

            if sources:
                # Select source
                source_titles = [f"{src.title} (ID: {src.id})" for src in sources]
                selected_source_title = st.selectbox(
                    "Select the document to delete:",
                    source_titles,
                    key="delete_source_select",
                )

                # Extract ID from selected source
                selected_source_id = int(
                    selected_source_title.split("ID: ")[1].split(")")[0]
                )

                # Confirmation
                confirm_source = st.checkbox(
                    f"⚠️ I confirm that I want to delete this document",
                    key="confirm_source_delete",
                )

                if st.button("❌ Delete Document", disabled=not confirm_source):
                    try:
                        delete_source(selected_source_id)
                        st.success("✅ Document deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error deleting document: {str(e)}")
                        logger.error(f"Error deleting source {selected_source_id}: {e}")
            else:
                st.info("No documents in this collection.")
        else:
            st.info("No collections available.")

    with tab2:
        st.markdown("**Delete a complete collection with all its documents:**")
        st.warning(
            "⚠️ This action will delete ALL documents from the selected collection."
        )

        if collections:
            # Select collection to delete
            collection_to_delete = st.selectbox(
                "Select the collection to delete:",
                collection_names,
                key="delete_collection_select",
            )

            # Show information about what will be deleted
            selected_col = next(
                col for col in collections if col.name == collection_to_delete
            )
            sources_in_col = get_all_source_in_collection(selected_col.name)

            st.info(f"📊 This collection contains {len(sources_in_col)} document(s)")

            # Multiple confirmations for greater safety
            confirm1 = st.checkbox(
                f"⚠️ I understand that {len(sources_in_col)} document(s) will be deleted",
                key="confirm_collection_1",
            )

            confirm2 = st.checkbox(
                f"⚠️ I confirm that I want to delete the collection '{collection_to_delete}'",
                key="confirm_collection_2",
            )

            if st.button(
                "❌ Delete Complete Collection",
                disabled=not (confirm1 and confirm2),
                type="secondary",
            ):
                try:
                    delete_collection(collection_to_delete)
                    st.success("✅ Collection deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting collection: {str(e)}")
                    logger.error(
                        f"Error deleting collection {collection_to_delete}: {e}"
                    )
        else:
            st.info("No collections available.")
