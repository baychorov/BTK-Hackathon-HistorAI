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

# App İçindeki Modüller
from app.services.config import ConfigManager
from app.database.database import DatabaseService
from app.services.gemini_manager import GeminiManager
from app.services.export_manager import ExportManager
from app.ui.view import render_app

# 1. Ortam Değişkenlerini Yükle (Yeni izole konumdan)
load_dotenv(dotenv_path="credentials/api_key.env")

# 2. Konfigürasyon Yöneticisini Başlat
config = ConfigManager()

# 3. Streamlit Sayfa Yapılandırması (TOML dosyasından çekiliyor)
# NOT: st.set_page_config diğer tüm Streamlit komutlarından önce çağrılmalıdır.
st.set_page_config(
    page_title=config.app.title,
    page_icon=config.app.icon,
    layout=config.app.layout
)

# 4. Persistent Session ID Üretici
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


# 5. Servislerin Başlatılması (Dependency Injection & Caching)
@st.cache_resource
def init_services():
    """
    Uygulama servislerini tek bir noktada ayağa kaldırır ve cache'ler.
    Böylece her sayfa etkileşiminde veritabanı veya API tekrar tekrar bağlanmaz.
    """
    # Veritabanı servisini TOML'daki db_path ile başlat
    db_service = DatabaseService(db_path=config.database.db_path)
    
    # Gemini AI servisini TOML'daki model ve prompt yolları ile başlat
    ai_service = GeminiManager(
        model_name=config.ai.model_name, 
        prompts_path=config.ai.prompts_path
    )
    
    # Export servisine db_service'i ve export konfigürasyonlarını enjekte et
    export_service = ExportManager(
        db_service=db_service,
        export_config=config.export
    )
    
    return db_service, ai_service, export_service


# Servisleri başlatıp değişkenlere alıyoruz
db_service, ai_service, export_service = init_services()


# 6. Session State İlklendirmesi
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


# 7. Uygulama Arayüzünü Tetikle
# Tüm UI çizim ve iş mantığı yönlendirmesini UI katmanındaki view.py üstlenir.
render_app(
    db_service=db_service, 
    ai_service=ai_service, 
    export_service=export_service
)