"""
This module contains reusable UI components for the HistorAI Streamlit application.
It includes the sidebar for chat history, header navigation, and export buttons.
"""

import streamlit as st

def render_header():
    """Üst bilgi ve anasayfa yönlendirme butonunu çizer."""
    col_home, col_title = st.columns([1, 10])
    
    with col_home:
        if st.button("🏠", help="Anasayfaya dön"):
            st.session_state.current_page = "home"
            st.session_state.current_conversation_id = None
            st.session_state.current_character = ""
            st.session_state.messages = []
            st.session_state.time_travel_active = False
            st.rerun()

    with col_title:
        st.title("🧙‍♂ HistorAI - Tarihi Karakter Chatbotu")


def render_sidebar(db_service, ai_service):
    """Yan menüyü (Geçmiş sohbetler, pinleme, silme, özet) çizer."""
    with st.sidebar:
        st.header("📚 Geçmiş Sohbetler")

        # Filtreleme
        filter_char = st.text_input("Karaktere göre filtrele")

        # Veritabanından sohbetleri getir
        conversations = db_service.get_conversations(
            session_id=st.session_state.user_session_id,
            filter_char=filter_char if filter_char else None
        )

        # Sohbet Listesi
        for conv_id, char, title, is_pinned, conv_type in conversations:
            pin_icon = "📌 " if is_pinned else ""
            type_icon = "⏰ " if conv_type == "time_travel" else ""
            label = f"{pin_icon}{type_icon}{char}: {title[:20]}..."

            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                # Sohbete git butonu
                if st.button(label, key=f"conv_{conv_id}"):
                    st.session_state.current_conversation_id = conv_id
                    st.session_state.current_character = char
                    st.session_state.current_page = "chat"
                    
                    # Mevcut sohbetin mesajlarını yükle
                    messages = db_service.get_messages(conv_id, st.session_state.user_session_id)
                    st.session_state.messages = []
                    for q, a in messages:
                        st.session_state.messages.append({"role": "user", "content": q})
                        st.session_state.messages.append({"role": "assistant", "content": a})
                    st.rerun()

            with col2:
                # Pin/Unpin butonu
                pin_text = "📌" if not is_pinned else "📍"
                if st.button(pin_text, key=f"pin_{conv_id}"):
                    # Durumu tersine çevirerek güncelle
                    db_service.toggle_pin_status(conv_id, not is_pinned, st.session_state.user_session_id)
                    st.rerun()

            with col3:
                # Sil butonu
                if st.button("🗑", key=f"del_{conv_id}"):
                    db_service.delete_conversation(conv_id, st.session_state.user_session_id)
                    if st.session_state.current_conversation_id == conv_id:
                        st.session_state.current_conversation_id = None
                        st.session_state.messages = []
                        st.session_state.current_page = "home"
                    st.rerun()

        st.divider()

        # Yeni sohbet başlat
        if st.button("✨ Yeni Sohbet Başlat"):
            st.session_state.current_conversation_id = None
            st.session_state.current_character = ""
            st.session_state.messages = []
            st.session_state.current_page = "home"
            st.session_state.time_travel_active = False
            if "conversation_summary" in st.session_state:
                del st.session_state.conversation_summary
            st.rerun()

        # Tüm geçmişi sil
        if st.button("🧨 Tüm Geçmişi Sil"):
            db_service.delete_all_history(st.session_state.user_session_id)
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.session_state.current_page = "home"
            st.rerun()

        st.divider()

        # Sohbet Özeti Oluşturma (Sadece aktif bir sohbet varsa)
        if st.session_state.current_conversation_id and len(st.session_state.messages) >= 2:
            st.subheader("📋 Sohbet Özeti")

            if st.button("🔍 Teknik Özet Oluştur"):
                with st.spinner("Özet oluşturuluyor..."):
                    summary = ai_service.create_conversation_summary(
                        st.session_state.messages,
                        st.session_state.current_character
                    )
                    st.session_state.conversation_summary = summary

            # Eğer özet daha önceden oluşturulmuşsa göster
            if st.session_state.get("conversation_summary"):
                with st.expander("📖 Tarihsel Özet", expanded=True):
                    st.markdown(st.session_state.conversation_summary)
                    if st.button("🗑️ Özeti Temizle", key="sidebar_clear_summary"):
                        del st.session_state.conversation_summary
                        st.rerun()
            st.divider()


def render_download_options(export_service):
    """Mevcut sohbet için PDF, Word ve JSON indirme butonlarını çizer."""
    if st.session_state.current_conversation_id:
        st.subheader("📥 İndirme Seçenekleri")
        st.write("Mevcut sohbeti indir:")

        col1, col2, col3 = st.columns(3)
        
        # Gerekli parametreleri session_state'ten topla
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