"""
This module serves as the thin orchestrator of the application.
It initializes configuration, services, manages session state, 
and delegates UI rendering to the UI layer.
"""

import random
import time
import uuid
import streamlit as st
from dotenv import load_dotenv

# Application modules
from app.services.config import ConfigManager
from app.database.database import DatabaseService
from app.services.gemini_manager import GeminiManager
from app.services.export_manager import ExportManager
from app.ui.view import render_app

# Load environment variables
load_dotenv(dotenv_path="credentials/api_key.env")

# Initialize configuration
config = ConfigManager()

# Streamlit page configuration
st.set_page_config(
    page_title=config.app.title,
    page_icon=config.app.icon,
    layout=config.app.layout
)


def get_persistent_session_id() -> str:
    """Generates a persistent session ID using query parameters or a random fallback."""
    try:
        if "session" in st.query_params:
            return st.query_params["session"]
        else:
            new_session = f"user_{int(time.time())}_{random.randint(1000, 9999)}"
            st.query_params.session = new_session
            return new_session
    except Exception:
        return str(uuid.uuid4())


@st.cache_resource
def init_services():
    """Initializes and caches core application services."""
    db_service = DatabaseService(db_path=config.database.db_path)
    
    ai_service = GeminiManager(
        model_name=config.ai.model_name, 
        prompts_path=config.ai.prompts_path
    )
    
    export_service = ExportManager(
        db_service=db_service,
        export_config=config.export
    )
    
    return db_service, ai_service, export_service


db_service, ai_service, export_service = init_services()


def init_session_state():
    """Initializes Streamlit session state variables."""
    if "user_session_id" not in st.session_state:
        st.session_state.user_session_id = get_persistent_session_id()
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    if "current_character" not in st.session_state:
        st.session_state.current_character = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"
    if "time_travel_active" not in st.session_state:
        st.session_state.time_travel_active = False


init_session_state()

# Render UI layer
render_app(
    db_service=db_service, 
    ai_service=ai_service, 
    export_service=export_service
)