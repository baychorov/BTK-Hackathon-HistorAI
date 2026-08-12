"""
This module contains the main views for the HistorAI application,
handling the routing between the home page and the active chat page.
"""

import streamlit as st
from app.models.data_structures import HISTORICAL_EVENTS, PERSONALITY_TEST
from app.ui.components import render_header, render_sidebar, render_download_options


def render_app(db_service, ai_service, export_service):
    """Handles the main layout and view routing."""
    render_header()
    render_sidebar(db_service, ai_service)

    if st.session_state.current_page == "home" and not st.session_state.current_conversation_id:
        render_home_page(db_service, ai_service)
    elif st.session_state.current_page == "chat" or st.session_state.current_conversation_id:
        render_chat_page(db_service, ai_service, export_service)


def render_home_page(db_service, ai_service):
    """Renders the home page including recommendations, time travel, and personality test."""
    
    # Character recommendations based on chat history
    if len(st.session_state.messages) >= 4:
        suggestion = ai_service.analyze_conversation_style(st.session_state.messages)
        if suggestion:
            st.markdown("---")
            st.markdown("### 🎯 Recommended Character")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info(f"**{suggestion['name']}** - {suggestion['reason']}")
            with col2:
                if st.button(f"💬 Chat with {suggestion['name']}", key="suggestion_chat"):
                    st.session_state.current_character = suggestion['name']
                    conv_id = db_service.create_conversation(
                        character=suggestion['name'], 
                        title=f"Chat with {suggestion['name']}", 
                        conv_type="normal", 
                        session_id=st.session_state.user_session_id
                    )
                    st.session_state.current_conversation_id = conv_id
                    st.session_state.current_page = "chat"
                    st.rerun()

    # Time Travel feature
    st.markdown("---")
    st.markdown("### ⏰ Time Travel - Reenact History")
    st.markdown("*Travel back to key historical moments and interact with key figures.*")

    if not st.session_state.time_travel_active:
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_year = st.selectbox(
                "Select a historical event:",
                options=list(HISTORICAL_EVENTS.keys()),
                format_func=lambda x: f"{x} - {HISTORICAL_EVENTS[x]['event']} ({HISTORICAL_EVENTS[x]['date']})"
            )

            if st.button("🚀 Start Time Travel", type="primary"):
                st.session_state.time_travel_active = True
                st.session_state.selected_event = selected_year
                st.rerun()

        with col2:
            st.markdown("#### 🎭 Experience:")
            st.markdown("🎬 Cinematic entry  \n👥 Character matching  \n🌍 Atmospheric context  \n🎯 Interactive roleplay")

    else:
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
            <h3>🎬 Time Travel Journey...</h3>
            <p style="font-size: 16px; line-height: 1.6;"><strong>Setting:</strong> {event_data['setting']}</p>
            <p style="font-size: 18px; font-style: italic; margin-top: 20px;">"{event_data['opening']}"</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 👥 Choose a character to meet:")
        selected_character = st.radio("Select character:", event_data['characters'], horizontal=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎭 Start Chat with Character", type="primary"):
                st.session_state.current_character = selected_character
                
                conv_id = db_service.create_conversation(
                    character=selected_character,
                    title=f"{event_data['event']} - {selected_character}",
                    conv_type="time_travel",
                    session_id=st.session_state.user_session_id
                )
                st.session_state.current_conversation_id = conv_id
                
                opening_message = f"Time traveling to {event_data['event']} on {event_data['date']}. {event_data['opening']}"
                st.session_state.messages = [{"role": "user", "content": opening_message}]
                
                st.session_state.time_travel_active = False
                st.session_state.current_page = "chat"
                st.rerun()

        with col1:
            if st.button("↩ Back"):
                st.session_state.time_travel_active = False
                st.rerun()

    # Personality Test
    st.markdown("---")
    
    if "test_active" not in st.session_state: st.session_state.test_active = False
    if "test_completed" not in st.session_state: st.session_state.test_completed = False
    if "test_question_index" not in st.session_state: st.session_state.test_question_index = 0
    if "test_scores" not in st.session_state: st.session_state.test_scores = {"openness": 0, "conscientiousness": 0, "extraversion": 0, "agreeableness": 0, "neuroticism": 0}

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🧬 Historical Personality Test")
        st.markdown("*Find out which historical figure matches your personality.*")

        if not st.session_state.test_active and not st.session_state.test_completed:
            if st.button("🚀 Start Test", type="primary"):
                st.session_state.test_active = True
                st.session_state.test_question_index = 0
                st.session_state.test_scores = {k: 0 for k in st.session_state.test_scores}
                st.rerun()

    with col2:
        st.markdown("#### 🎯 Results include:")
        st.markdown("✨ Character matching  \n📊 Compatibility score  \n💬 Instant chat launch")

    if st.session_state.test_active:
        current_q = st.session_state.test_question_index
        total_q = len(PERSONALITY_TEST["questions"])

        if current_q < total_q:
            st.markdown("---")
            st.progress((current_q) / total_q, text=f"Question {current_q + 1} / {total_q}")

            question_data = PERSONALITY_TEST["questions"][current_q]
            st.markdown(f"### 📝 Question {current_q + 1}")
            st.markdown(f"{question_data['question']}")

            option_labels = [opt["text"] for opt in question_data["options"]]
            selected_option = st.radio("Select answer:", options=range(len(option_labels)), format_func=lambda x: option_labels[x], key=f"test_q_{current_q}")

            col1, col2, col3 = st.columns([1, 1, 2])
            with col2:
                if st.button("➡ Next Question", type="primary"):
                    selected_traits = question_data["options"][selected_option]["traits"]
                    for trait, score in selected_traits.items():
                        st.session_state.test_scores[trait] += score
                    st.session_state.test_question_index += 1
                    st.rerun()
            with col1:
                if st.button("❌ Cancel Test"):
                    st.session_state.test_active = False
                    st.session_state.test_question_index = 0
                    st.rerun()
        else:
            st.session_state.test_active = False
            st.session_state.test_completed = True
            st.rerun()

    if st.session_state.test_completed:
        st.markdown("---")
        st.markdown("## 🎉 Test Results")

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
                    <h2>🏆 Top Match!</h2>
                    <h1>{character['name']}</h1>
                    <h2>{percentage:.0f}% Match</h2>
                    <p style="font-style: italic;">"{character['quote']}"</p>
                    <p>{character['description']}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button(f"💬 Chat with {character['name']}", type="primary", key="start_chat_best"):
                        st.session_state.current_character = character['name']
                        conv_id = db_service.create_conversation(
                            character['name'], 
                            f"Personality Test Chat with {character['name']}", 
                            "personality", 
                            st.session_state.user_session_id
                        )
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.test_completed = False
                        st.session_state.current_page = "chat"
                        st.rerun()
            else:
                with st.expander(f"#{i + 1} - {character['name']} ({percentage:.0f}% match)"):
                    st.markdown(f"{character['description']}")
                    st.markdown(f"\"{character['quote']}\"")
                    if st.button(f"💬 Chat with {character['name']}", key=f"start_chat_{i}"):
                        st.session_state.current_character = character['name']
                        conv_id = db_service.create_conversation(
                            character['name'], 
                            f"Personality Test Chat with {character['name']}", 
                            "personality", 
                            st.session_state.user_session_id
                        )
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.test_completed = False
                        st.session_state.current_page = "chat"
                        st.rerun()

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Retake Test"):
                st.session_state.test_active = False
                st.session_state.test_completed = False
                st.session_state.test_question_index = 0
                st.rerun()
        with col2:
            if st.button("➡ Select Character Manually"):
                st.session_state.test_completed = False
                st.rerun()

    # Manual character selection
    if not st.session_state.test_active and not st.session_state.test_completed:
        st.markdown("---")
        st.markdown("### 🎭 Select Character Manually")
        character = st.text_input("Enter character name:", placeholder="e.g. Leonardo da Vinci, Socrates, Cleopatra...")

        if character:
            st.session_state.current_character = character
            conv_id = db_service.create_conversation(
                character, 
                f"Chat with {character}", 
                "manual", 
                st.session_state.user_session_id
            )
            st.session_state.current_conversation_id = conv_id
            st.session_state.current_page = "chat"
            st.rerun()


def render_chat_page(db_service, ai_service, export_service):
    """Renders active chat interface and manages message flow."""
    st.markdown(f"### 🗣 Chatting with {st.session_state.current_character}")

    # Mid-chat suggestion
    if len(st.session_state.messages) >= 6:
        suggestion = ai_service.analyze_conversation_style(st.session_state.messages)
        if suggestion and suggestion['name'] != st.session_state.current_character:
            with st.expander("🎯 New Character Recommendation Available", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"**{suggestion['name']}** - {suggestion['reason']}")
                with col2:
                    if st.button(f"💬 {suggestion['name']}", key="mid_chat_suggestion"):
                        if st.session_state.messages:
                            first_q = st.session_state.messages[0]["content"] if st.session_state.messages[0]["role"] == "user" else "Chat"
                            title = first_q[:50] + "..." if len(first_q) > 50 else first_q
                            db_service.update_conversation_title(st.session_state.current_conversation_id, title, st.session_state.user_session_id)

                        st.session_state.current_character = suggestion['name']
                        conv_id = db_service.create_conversation(
                            suggestion['name'], 
                            f"Recommended Chat with {suggestion['name']}", 
                            "suggestion", 
                            st.session_state.user_session_id
                        )
                        st.session_state.current_conversation_id = conv_id
                        st.session_state.messages = []
                        st.rerun()

    # Render message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Display active summary
    if st.session_state.get("conversation_summary"):
        st.markdown("---")
        with st.expander("📖 Conversation Summary", expanded=False):
            st.markdown(st.session_state.conversation_summary)
            if st.button("🗑️ Clear Summary", key="main_clear_summary"):
                del st.session_state.conversation_summary
                st.rerun()

    # Chat input and response generation
    if prompt := st.chat_input("Type your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                is_time_travel = len(st.session_state.messages) == 1 and "Time traveling" in st.session_state.messages[0]["content"]
                
                answer = ai_service.generate_chat_response(prompt, st.session_state.current_character, is_time_travel)
                st.write(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})
                db_service.add_message(
                    st.session_state.current_conversation_id, 
                    prompt, 
                    answer, 
                    st.session_state.user_session_id
                )

    # Chat controls
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("✅ End Chat"):
            if st.session_state.messages:
                first_q = st.session_state.messages[0]["content"] if st.session_state.messages[0]["role"] == "user" else "Chat"
                title = first_q[:50] + "..." if len(first_q) > 50 else first_q
                db_service.update_conversation_title(st.session_state.current_conversation_id, title, st.session_state.user_session_id)

            st.session_state.current_conversation_id = None
            st.session_state.current_character = ""
            st.session_state.messages = []
            st.session_state.current_page = "home"
            st.success("Chat ended and saved to history!")
            st.rerun()
            
    with col2:
        if st.button("📋 Generate Summary") and len(st.session_state.messages) >= 2:
            with st.spinner("Generating summary..."):
                summary = ai_service.create_conversation_summary(st.session_state.messages, st.session_state.current_character)
                st.session_state.conversation_summary = summary
                st.rerun()

    render_download_options(export_service)