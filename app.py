"""
This module serves as the thin orchestrator of the application.
It initializes services, manages session state, and delegates UI rendering
to the UI layer.
"""

import random
import time
import uuid
import streamlit as st
from dotenv import load_dotenv

# App İçindeki Modüller
from app.database.database import DatabaseService
from app.services.gemini_manager import GeminiManager
from app.services.export_manager import ExportManager
from app.ui.view import render_app


# 1. Ortam Değişkenlerini Yükle
load_dotenv()

# 2. Streamlit Sayfa Yapılandırması (Tüm Streamlit kodlarından önce gelmeli)
st.set_page_config(
    page_title="HistorAI",
    page_icon="🧙‍♂",
    layout="wide"
)


# 3. Persistent Session ID Üretici
def get_persistent_session_id() -> str:
    """Tarayıcı parametrelerine dayalı veya rastgele benzersiz oturum kimliği üretir."""
    try:
        if "session" in st.query_params:
            return st.query_params["session"]
        else:
            new_session = f"user_{int(time.time())}_{random.randint(1000, 9999)}"
            st.query_params.session = new_session
            return new_session
    except Exception:
        return str(uuid.uuid4())


# 4. Servislerin Başlatılması (Dependency Injection & Caching)
@st.cache_resource
def init_services():
    """
    Uygulama servislerini tek bir noktada ayağa kaldırır ve cache'ler.
    Böylece her sayfa etkileşiminde veritabanı veya API tekrar tekrar bağlanmaz.
    """
    db_service = DatabaseService(db_path="app/database/historai.db")
    
    ai_service = GeminiManager(
        model_name="gemini-2.5-flash", 
        prompts_path="app/prompts/prompts.json"
    )
    
    # Export service'e veritabanı servisini enjekte ediyoruz
    export_service = ExportManager(db_service=db_service)
    
    return db_service, ai_service, export_service


# Servisleri al
db_service, ai_service, export_service = init_services()


# 5. Session State İlklendirmesi
def init_session_state():
    """Streamlit oturum durum değişkenlerini varsayılan değerlerle başlatır."""
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


# 6. Uygulama Arayüzünü Tetikle
# Tüm UI çizim ve iş mantığı yönlendirmesini UI katmanındaki view.py üstlenir.
render_app(
    db_service=db_service, 
    ai_service=ai_service, 
    export_service=export_service
)