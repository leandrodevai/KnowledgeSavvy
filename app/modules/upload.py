"""
KnowledgeSavvy - Document Upload Module

This module provides the interface for uploading documents and URLs to the knowledge base.
It handles file processing, web scraping, and document vectorization with configurable
chunk sizes and overlap settings.


"""

import logging

import streamlit as st

logger = logging.getLogger(__name__)

from core import ingestion
from database import crud


def upload_interface():
    """
    Main interface for uploading documents and URLs.

    This function:
    1. Provides options for document upload or URL web scraping
    2. Configures chunk size and overlap parameters
    3. Handles file uploads with preview functionality
    4. Processes URLs with configurable scraping depth
    5. Manages the upload process with progress tracking
    """
    file_or_url = st.radio(
        "Upload document or URL for web scraping", ("Document", "URL")
    )
    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.slider("Chunk size:", 1000, 10000, 4000, 500)
    with col2:
        chunk_overlap = st.slider("Chunk overlap:", 0, 500, 200, 50)

    if not st.session_state.current_collection:
        st.warning("⚠️ Select a collection to proceed")
        return

    if file_or_url == "URL":
        st.header("📤 Upload URL")
        url = st.text_input("Enter the URL:")
        scraping_depth = st.slider(
            "Scraping depth:", 1, 5, 2, 1, help="Web search depth"
        )
        if st.button("📥 Upload URL"):
            if url:
                sources = crud.get_all_source_in_collection(
                    st.session_state.current_collection
                )
                source_title = [src.title for src in sources] if sources else []
                if url in source_title:
                    st.warning(
                        "⚠️ This URL has already been uploaded to the current collection"
                    )
                with st.spinner("Processing the URL..."):
                    num_chunks = ingestion.process_url(
                        url=url,
                        collection_name=st.session_state.current_collection,
                        depth=scraping_depth,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                    )
                if num_chunks > 0:
                    st.success(
                        f"✅ {num_chunks} chunks from the URL uploaded successfully to collection: **{st.session_state.current_collection}**"
                    )
                if num_chunks == 0:
                    st.warning(
                        "ℹ️ No chunks were generated. Check the URL or scraping depth."
                    )
            else:
                st.error("⚠️ Please enter a valid URL.")
            if st.button("Accept"):
                st.rerun()

    if file_or_url == "Document":
        st.header("📤 Upload Documents")
        st.info(
            f"📁 Uploading to collection: **{st.session_state.current_collection}**"
        )

        # File uploader
        uploaded_files = st.file_uploader(
            "Select files:",
            type=["pdf", "txt", "docx", "md"],
            accept_multiple_files=True,
            help="Supported formats: PDF, TXT, DOCX, MD",
        )
        # doc_name = st.text_input("Document name:", value=uploaded_files[0].name if uploaded_files else "")

        if uploaded_files:
            st.write(f"📎 {len(uploaded_files)} file(s) selected")

            # Show file previews
            for file in uploaded_files:
                with st.expander(f"📄 {file.name} ({file.size / 1024:.1f} KB)"):
                    if file.type == "text/plain":
                        # Preview for text files
                        content = str(file.read(), "utf-8")
                        st.text_area(
                            "Preview:",
                            content[:500] + "..." if len(content) > 500 else content,
                        )
                        file.seek(0)  # Reset file pointer
                    else:
                        st.write(f"Type: {file.type}")

            # Processing button
            if st.button("🚀 Process and Vectorize", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                with st.spinner("Please wait..."):
                    try:
                        # vector_manager = VectorStoreManager()

                        for i, file in enumerate(uploaded_files):
                            status_text.text(f"Processing {file.name}...")
                            progress_bar.progress((i + 1) / len(uploaded_files))

                            # Here you would call your document processor
                            # vector_manager.add_document(file, st.session_state.current_collection)
                            num_chunks = ingestion.process_documents(
                                file=file,
                                collection_name=st.session_state.current_collection,
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap,
                            )
                            st.success(
                                f"✅ {file.name} processed with {num_chunks} chunks"
                            )

                            # Simulate processing
                            import time

                            time.sleep(1)

                        st.success(
                            f"✅ {len(uploaded_files)} files processed successfully!"
                        )
                        st.balloons()  # Visual celebration effect

                    except Exception as e:
                        st.error(f"❌ Error processing files: {e}")
                    finally:
                        progress_bar.empty()
                        status_text.empty()
