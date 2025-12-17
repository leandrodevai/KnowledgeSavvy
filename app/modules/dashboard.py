"""
KnowledgeSavvy - Dashboard Module

This module provides a comprehensive dashboard for monitoring and analyzing
the knowledge base. It displays statistics, collection information, and
document distribution across collections.


"""

import logging

import pandas as pd
import streamlit as st

from database.crud import get_all_collections, get_all_source_in_collection

logger = logging.getLogger(__name__)


def dashboard_interface():
    """
    Main dashboard interface displaying knowledge base statistics and analytics.

    This function:
    1. Shows general metrics (collections, documents, etc.)
    2. Displays collection information in a table format
    3. Creates visual charts for document distribution
    4. Shows sources per collection with detailed metadata
    5. Provides an overview of the entire knowledge base
    """
    st.header("📊 Dashboard")

    # General metrics
    collections = get_all_collections()
    total_docs = sum(col.document_count for col in collections) if collections else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Collections", len(collections))
    with col2:
        st.metric("Total Documents", total_docs)
    # with col3:
    # st.metric("Queries Today", len(st.session_state.chat_history))
    # with col4:
    #     avg_confidence = 0.85  # Calculate real average
    #     st.metric("Average Confidence", f"{avg_confidence:.1%}")

    if collections:
        # Collections table
        st.subheader("📁 Existing Collections")

        df_data = []
        for col in collections:
            df_data.append(
                {
                    "Name": col.name,
                    "Documents": col.document_count,
                    "Created": col.created_at.strftime("%d/%m/%Y"),
                    "Description": col.description or "No description",
                }
            )

        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True)

        # Document distribution chart
        st.subheader("📈 Document Distribution")
        chart_data = pd.DataFrame(
            {
                "Collection": [col.name for col in collections],
                "Documents": [col.document_count for col in collections],
            }
        )
        st.bar_chart(chart_data.set_index("Collection"))

        # New section: Sources per collection
        st.subheader("📂 Sources per Collection")
        for col in collections:
            with st.expander(f"Sources in '{col.name}'"):
                sources = get_all_source_in_collection(col.name)
                if sources:
                    source_data = []
                    for src in sources:
                        source_data.append(
                            {
                                "Source Name": src.title,
                                "Type": src.type,
                                "Uploaded": src.uploaded_at.strftime("%d/%m/%Y"),
                                # "N° Chunks": len(src.ids)
                            }
                        )
                    source_df = pd.DataFrame(source_data)
                    st.dataframe(source_df, use_container_width=True)
                else:
                    st.info(f"No sources in collection '{col.name}'.")

    else:
        st.info(
            "No collections created yet. Create your first collection to get started!"
        )
