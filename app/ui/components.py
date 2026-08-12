"""
This module contains reusable UI components for the HistorAI Streamlit application.
It includes the sidebar for chat history, header navigation, and export buttons.
"""

import streamlit as st

def render_header():
    """Renders the header navigation bar and home button."""
    col_home, col_title = st.columns([1, 10])
    
    with col_home:
        if st.button("🏠", help="Return to home"):
            st.session_state.current_page = "home"
            st.session_state.current_conversation_id = None
            st.session_state.current_character = ""
            st.session_state.messages = []
            st.session_state.time_travel_active = False
            st.rerun()

    with col_title:
        st.title("🧙‍♂ HistorAI - Historical Character Chatbot")


def render_sidebar(db_service, ai_service):
    """Renders the sidebar containing chat history, actions, and summary generator."""
    with st.sidebar:
        st.header("📚 Chat History")

        filter_char = st.text_input("Filter by character")

        conversations = db_service.get_conversations(
            session_id=st.session_state.user_session_id,
            filter_char=filter_char if filter_char else None
        )

        for conv_id, char, title, is_pinned, conv_type in conversations:
            pin_icon = "📌 " if is_pinned else ""
            type_icon = "⏰ " if conv_type == "time_travel" else ""
            label = f"{pin_icon}{type_icon}{char}: {title[:20]}..."

            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                if st.button(label, key=f"conv_{conv_id}"):
                    st.session_state.current_conversation_id = conv_id
                    st.session_state.current_character = char
                    st.session_state.current_page = "chat"
                    
                    messages = db_service.get_messages(conv_id, st.session_state.user_session_id)
                    st.session_state.messages = []
                    for q, a in messages:
                        st.session_state.messages.append({"role": "user", "content": q})
                        st.session_state.messages.append({"role": "assistant", "content": a})
                    st.rerun()

            with col2:
                pin_text = "📌" if not is_pinned else "📍"
                if st.button(pin_text, key=f"pin_{conv_id}"):
                    db_service.toggle_pin_status(conv_id, not is_pinned, st.session_state.user_session_id)
                    st.rerun()

            with col3:
                if st.button("🗑", key=f"del_{conv_id}"):
                    db_service.delete_conversation(conv_id, st.session_state.user_session_id)
                    if st.session_state.current_conversation_id == conv_id:
                        st.session_state.current_conversation_id = None
                        st.session_state.messages = []
                        st.session_state.current_page = "home"
                    st.rerun()

        st.divider()

        if st.button("✨ Start New Chat"):
            st.session_state.current_conversation_id = None
            st.session_state.current_character = ""
            st.session_state.messages = []
            st.session_state.current_page = "home"
            st.session_state.time_travel_active = False
            if "conversation_summary" in st.session_state:
                del st.session_state.conversation_summary
            st.rerun()

        if st.button("🧨 Clear All History"):
            db_service.delete_all_history(st.session_state.user_session_id)
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.session_state.current_page = "home"
            st.rerun()

        st.divider()

        if st.session_state.current_conversation_id and len(st.session_state.messages) >= 2:
            st.subheader("📋 Conversation Summary")

            if st.button("🔍 Generate Summary"):
                with st.spinner("Generating summary..."):
                    summary = ai_service.create_conversation_summary(
                        st.session_state.messages,
                        st.session_state.current_character
                    )
                    st.session_state.conversation_summary = summary

            if st.session_state.get("conversation_summary"):
                with st.expander("📖 Historical Summary", expanded=True):
                    st.markdown(st.session_state.conversation_summary)
                    if st.button("🗑️ Clear Summary", key="sidebar_clear_summary"):
                        del st.session_state.conversation_summary
                        st.rerun()
            st.divider()


def render_download_options(export_service):
    """Renders PDF, Word, and JSON download buttons for the active conversation."""
    if st.session_state.current_conversation_id:
        st.subheader("📥 Export Options")
        st.write("Download current conversation:")

        col1, col2, col3 = st.columns(3)
        
        conv_id = st.session_state.current_conversation_id
        session_id = st.session_state.user_session_id
        char_name = st.session_state.current_character
        summary = st.session_state.get("conversation_summary")

        with col1:
            try:
                pdf_data = export_service.create_pdf(conv_id, session_id, summary)
                if pdf_data:
                    st.download_button("📄 PDF", data=pdf_data,
                                       file_name=f"historai_{char_name}.pdf",
                                       mime="application/pdf")
            except Exception as e:
                st.error(str(e))

        with col2:
            try:
                word_data = export_service.create_word(conv_id, session_id, summary)
                if word_data:
                    st.download_button("📝 Word", data=word_data,
                                       file_name=f"historai_{char_name}.docx",
                                       mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            except Exception as e:
                st.error(str(e))

        with col3:
            try:
                json_data = export_service.create_json(conv_id, session_id, summary)
                if json_data:
                    st.download_button("🗂 JSON", data=json_data,
                                       file_name=f"historai_{char_name}.json",
                                       mime="application/json")
            except Exception as e:
                st.error(str(e))