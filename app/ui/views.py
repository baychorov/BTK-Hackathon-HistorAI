"""
This module contains the main views for the HistorAI application,
handling the routing between the home page and the active chat page.
"""

import streamlit as st
from app.models.data_structures import HISTORICAL_EVENTS, PERSONALITY_TEST
from app.ui.components import render_header, render_sidebar, render_download_options


def render_app(db_service, ai_service, export_service):
    """Uygulamanın ana iskeletini ve sayfa yönlendirmelerini yönetir."""
    
    # 1. Ortak Bileşenleri Çiz (Header ve Sidebar)
    render_header()
    render_sidebar(db_service, ai_service)

    # 2. Sayfa Yönlendirmesi (Routing)
    if st.session_state.current_page == "home" and not st.session_state.current_conversation_id:
        render_home_page(db_service, ai_service)
    elif st.session_state.current_page == "chat" or st.session_state.current_conversation_id:
        render_chat_page(db_service, ai_service, export_service)


def render_home_page(db_service, ai_service):
    """Anasayfayı (Tavsiyeler, Zamanda Yolculuk, Kişilik Testi) çizer."""
    
    # --- KARAKTER TAVSİYESİ (Geçmiş sohbet verisine dayanarak) ---
    if len(st.session_state.messages) >= 4:
        suggestion = ai_service.analyze_conversation_style(st.session_state.messages)
        if suggestion:
            st.markdown("---")
            st.markdown("### 🎯 Size Özel Karakter Tavsiyesi")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"**{suggestion['name']}** - {suggestion['reason']}")
            with col2:
                if st.button(f"💬 {suggestion['name']} ile sohbet et", key="suggestion_chat"):
                    st.session_state.current_character = suggestion['name']
                    conv_id = db_service.create_conversation(
                        character=suggestion['name'], 
                        title=f"{suggestion['name']} ile tavsiye sohbeti", 
                        conv_type="normal", 
                        session_id=st.session_state.user_session_id
                    )
                    st.session_state.current_conversation_id = conv_id
                    st.session_state.current_page = "chat"
                    st.rerun()

    # --- ZAMANDA YOLCULUK ---
    st.markdown("---")
    st.markdown("### ⏰ Zamanda Yolculuk - Olay Anı Canlandırma")
    st.markdown("*Tarihin en kritik anlarına gidip o dönemin karakterleriyle yaşayın!*")

    if not st.session_state.time_travel_active:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_year = st.selectbox(
                "Hangi tarihi olayın ortasına gitmek istersiniz?",
                options=list(HISTORICAL_EVENTS.keys()),
                format_func=lambda x: f"{x} - {HISTORICAL_EVENTS[x]['event']} ({HISTORICAL_EVENTS[x]['date']})"
            )

            if st.button("🚀 Zamanda Yolculuğa Başla", type="primary"):
                st.session_state.time_travel_active = True
                st.session_state.selected_event = selected_year
                st.rerun()

        with col2:
            st.markdown("#### 🎭 Deneyim:")
            st.markdown("🎬 Sinematik giriş  \n👥 Otomatik karakter eşleşmesi  \n🌍 Ortam betimlemesi  \n🎯 Interaktif roleplay")

    else:
        # Zamanda Yolculuk Aktif Ekranı
        event_data = HISTORICAL_EVENTS[st.session_state.selected_event]
        st.markdown(f"### 🌍 {event_data['event']} - {event_data['date']}")

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            padding: 25px;
            border-radius: 15px;
            color: white;
            margin: 20px 0;
            border-left: 5px solid #f39c12;
        ">
            <h3>🎬 Zamanda Yolculuk Başlıyor...</h3>
            <p style="font-size: 16px; line-height: 1.6;"><strong>Ortam:</strong> {event_data['setting']}</p>
            <p style="font-size: 18px; font-style: italic; margin-top: 20px;">"{event_data['opening']}"</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 👥 Bu olayda kiminle karşılaşmak istersiniz?")
        selected_character = st.radio("Karakter seçin:", event_data['characters'], horizontal=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎭 Bu Karakterle Sohbete Başla", type="primary"):
                st.session_state.current_character = selected_character
                
                conv_id = db_service.create_conversation(
                    character=selected_character,
                    title=f"{event_data['event']} - {selected_character}",
                    conv_type="time_travel",
                    session_id=st.session_state.user_session_id
                )
                st.session_state.current_conversation_id = conv_id
                
                # İlk mesajı otomatik ekle
                opening_message = f"Zamanda yolculuk yaparak {event_data['date']} tarihindeki {event_data['event']} olayının tam ortasındayım. {event_data['opening']}"
                st.session_state.messages = [{"role": "user", "content": opening_message}]
                
                st.session_state.time_travel_active = False
                st.session_state.current_page = "chat"
                st.rerun()

        with col1:
            if st.button("↩ Geri Dön"):
                st.session_state.time_travel_active = False
                st.rerun()

    # --- KİŞİLİK TESTİ ---
    st.markdown("---")
    
    # State tanımlamaları (varsa koru, yoksa oluştur)
    if "test_active" not in st.session_state: st.session_state.test_active = False
    if "test_completed" not in st.session_state: st.session_state.test_completed = False
    if "test_question_index" not in st.session_state: st.session_state.test_question_index = 0
    if "test_scores" not in st.session_state: st.session_state.test_scores = {"openness": 0, "conscientiousness": 0, "extraversion": 0, "agreeableness": 0, "neuroticism": 0}

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🧬 Tarihî Kişilik Testi")
        st.markdown("*5 soruluk kısa testle hangi tarihi karaktere benzediğinizi keşfedin!*")

        if not st.session_state.test_active and not st.session_state.test_completed:
            if st.button("🚀 Teste Başla", type="primary"):
                st.session_state.test_active = True
                st.session_state.test_question_index = 0
                st.session_state.test_scores = {k: 0 for k in st.session_state.test_scores}
                st.rerun()

    with col2:
        st.markdown("#### 🎯 Test Sonrası:")
        st.markdown("✨ Kişilik eşleşmesi  \n📊 Uyumluluk yüzdesi  \n💬 Direkt sohbet başlat")

    # Test Soruları
    if st.session_state.test_active:
        current_q = st.session_state.test_question_index
        total_q = len(PERSONALITY_TEST["questions"])

        if current_q < total_q:
            st.markdown("---")
            st.progress((current_q) / total_q, text=f"Soru {current_q + 1} / {total_q}")

            question_data = PERSONALITY_TEST["questions"][current_q]
            st.markdown(f"### 📝 Soru {current_q + 1}")
            st.markdown(f"{question_data['question']}")

            option_labels = [opt["text"] for opt in question_data["options"]]
            selected_option = st.radio("Seçiminizi yapın:", options=range(len(option_labels)), format_func=lambda x: option_labels[x], key=f"test_q_{current_q}")

            col1, col2, col3 = st.columns([1, 1, 2])
            with col2:
                if st.button("➡ Sonraki Soru", type="primary"):
                    selected_traits = question_data["options"][selected_option]["traits"]
                    for trait, score in selected_traits.items():
                        st.session_state.test_scores[trait] += score
                    st.session_state.test_question_index += 1
                    st.rerun()
            with col1:
                if st.button("❌ Testi Durdur"):
                    st.session_state.test_active = False
                    st.session_state.test_question_index = 0
                    st.rerun()
        else:
            st.session_state.test_active = False
            st.session_state.test_completed = True
            st.rerun()

    # Test Sonuçları
    if st.session_state.test_completed:
        st.markdown("---")
        st.markdown("## 🎉 Test Sonuçlarınız")

        normalized_scores = {}
        for trait, score in st.session_state.test_scores.items():
            max_possible = 10
            min_possible = -5
            normalized = ((score - min_possible) / (max_possible - min_possible)) * 10
            normalized_scores[trait] = max(0, min(10, normalized))

        matches = ai_service.calculate_personality_match(normalized_scores, PERSONALITY_TEST["characters"])

        for i, match in enumerate(matches[:3]):
            character = match["character"]
            percentage = match["percentage"]

            if i == 0:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; margin: 10px 0; text-align: center;">
                    <h2>🏆 En İyi Eşleşmeniz!</h2>
                    <h1>{character['name']}</h1>
                    <h2>%{percentage:.0f} Uyumluluk</h2>
                    <p style="font-style: italic;">"{character['quote']}"</p>
                    <p>{character['description']}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(f"💬 {character['name']} ile Sohbet Başlat", type="primary", key="start_chat_best"):
                        st.session_state.current_character = character['name']
                        conv_id = db_service.create_conversation(
                            character['name'], 
                            f"{character['name']} ile kişilik testi sohbeti", 
                            "personality", 
                            st.session_state.user_session_id
                        )
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.test_completed = False
                        st.session_state.current_page = "chat"
                        st.rerun()
            else:
                with st.expander(f"#{i + 1} - {character['name']} (%{percentage:.0f} uyumluluk)"):
                    st.markdown(f"{character['description']}")
                    st.markdown(f"\"{character['quote']}\"")
                    if st.button(f"💬 {character['name']} ile Sohbet Başlat", key=f"start_chat_{i}"):
                        st.session_state.current_character = character['name']
                        conv_id = db_service.create_conversation(
                            character['name'], 
                            f"{character['name']} ile kişilik testi sohbeti", 
                            "personality", 
                            st.session_state.user_session_id
                        )
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.test_completed = False
                        st.session_state.current_page = "chat"
                        st.rerun()

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Testi Tekrar Al"):
                st.session_state.test_active = False
                st.session_state.test_completed = False
                st.session_state.test_question_index = 0
                st.rerun()
        with col2:
            if st.button("➡ Manuel Karakter Seç"):
                st.session_state.test_completed = False
                st.rerun()

    # --- MANUEL KARAKTER SEÇİMİ ---
    if not st.session_state.test_active and not st.session_state.test_completed:
        st.markdown("---")
        st.markdown("### 🎭 Veya Manuel Karakter Seçin")
        character = st.text_input("Tarihi karakter adını girin:", placeholder="Örn: Fatih Sultan Mehmet, Leonardo da Vinci, Mevlana...")

        if character:
            st.session_state.current_character = character
            conv_id = db_service.create_conversation(
                character, 
                f"{character} ile sohbet", 
                "manual", 
                st.session_state.user_session_id
            )
            st.session_state.current_conversation_id = conv_id
            st.session_state.current_page = "chat"
            st.rerun()


def render_chat_page(db_service, ai_service, export_service):
    """Aktif sohbet ekranını ve mesajlaşma döngüsünü çizer."""
    
    st.markdown(f"### 🗣 {st.session_state.current_character} ile sohbet ediyorsunuz")

    # Orta sohbet tavsiyesi
    if len(st.session_state.messages) >= 6:
        suggestion = ai_service.analyze_conversation_style(st.session_state.messages)
        if suggestion and suggestion['name'] != st.session_state.current_character:
            with st.expander("🎯 Size başka bir karakter önerisi var!", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"**{suggestion['name']}** - {suggestion['reason']}")
                with col2:
                    if st.button(f"💬 {suggestion['name']}", key="mid_chat_suggestion"):
                        if st.session_state.messages:
                            first_q = st.session_state.messages[0]["content"] if st.session_state.messages[0]["role"] == "user" else "Sohbet"
                            title = first_q[:50] + "..." if len(first_q) > 50 else first_q
                            db_service.update_conversation_title(st.session_state.current_conversation_id, title, st.session_state.user_session_id)

                        st.session_state.current_character = suggestion['name']
                        conv_id = db_service.create_conversation(
                            suggestion['name'], 
                            f"{suggestion['name']} ile tavsiye sohbeti", 
                            "suggestion", 
                            st.session_state.user_session_id
                        )
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.messages = []
                        st.rerun()

    # Mesajları Ekrana Bas
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Özet Gösterimi
    if st.session_state.get("conversation_summary"):
        st.markdown("---")
        with st.expander("📖 Sohbet Özeti", expanded=False):
            st.markdown(st.session_state.conversation_summary)
            if st.button("🗑️ Özeti Temizle", key="main_clear_summary"):
                del st.session_state.conversation_summary
                st.rerun()

    # Kullanıcı Girdisi ve AI Yanıtı
    if prompt := st.chat_input("Sorunuzu yazın..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Yanıt oluşturuluyor..."):
                
                is_time_travel = len(st.session_state.messages) == 1 and "Zamanda yolculuk" in st.session_state.messages[0]["content"]
                
                # API'den Yanıt Al
                answer = ai_service.generate_chat_response(prompt, st.session_state.current_character, is_time_travel)
                st.write(answer)

                # Yanıtı state'e ve veritabanına kaydet
                st.session_state.messages.append({"role": "assistant", "content": answer})
                db_service.add_message(
                    st.session_state.current_conversation_id, 
                    prompt, 
                    answer, 
                    st.session_state.user_session_id
                )

    # Alt Kontroller (Bitir, Özet, İndirme)
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("✅ Sohbeti Bitir"):
            if st.session_state.messages:
                first_q = st.session_state.messages[0]["content"] if st.session_state.messages[0]["role"] == "user" else "Sohbet"
                title = first_q[:50] + "..." if len(first_q) > 50 else first_q
                db_service.update_conversation_title(st.session_state.current_conversation_id, title, st.session_state.user_session_id)

            st.session_state.current_conversation_id = None
            st.session_state.current_character = ""
            st.session_state.messages = []
            st.session_state.current_page = "home"
            st.success("Sohbet tamamlandı ve geçmişe kaydedildi!")
            st.rerun()
            
    with col2:
        if st.button("📋 Özet Oluştur") and len(st.session_state.messages) >= 2:
            with st.spinner("Özet oluşturuluyor..."):
                summary = ai_service.create_conversation_summary(st.session_state.messages, st.session_state.current_character)
                st.session_state.conversation_summary = summary
                st.rerun()

    # İndirme Seçenekleri Bileşeni
    render_download_options(export_service)