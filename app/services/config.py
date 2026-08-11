"""
This module reads the environment-based TOML configuration files 
and provides them as dataclass objects to the rest of the application.
"""

import os
import tomllib
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    title: str
    icon: str
    layout: str
    debug: bool
    environment: str

@dataclass
class DatabaseConfig:
    db_path: str

@dataclass
class AIConfig:
    model_name: str
    prompts_path: str
    temperature: float

@dataclass
class ExportConfig:
    fallback_font: str = "Helvetica"
    document_title: str = "HistorAI Sohbeti"
    pdf_title_color: str = "#1a365d"
    pdf_subtitle_color: str = "#2d3748"
    pdf_question_color: str = "#2b6cb0"
    pdf_answer_color: str = "#1a202c"
    word_question_color: list = field(default_factory=lambda: [43, 108, 176])
    word_answer_color: list = field(default_factory=lambda: [212, 84, 58])

class ConfigManager:
    """Singleton tasarım deseni ile konfigürasyonları sadece bir kez yükler."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config() # Sınıf çağrıldığında TOML dosyasını okuyan tetikleyici
        return cls._instance

    def _load_config(self):
        # .env dosyasında APP_ENV tanımlı değilse varsayılan olarak 'local' kabul et
        env = os.getenv("APP_ENV", "local")
        # main.py kök dizinde çalıştığı için yollar kök dizine göre verilir
        config_path = f"configs/config.{env}.toml"
        
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
                
            # İşte ConfigManager'a niteliklerin (attribute) eklendiği yer burası:
            self.app = AppConfig(**data.get("app", {}))
            self.database = DatabaseConfig(**data.get("database", {}))
            self.ai = AIConfig(**data.get("ai", {}))
            self.export = ExportConfig(**data.get("export", {}))
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {config_path}")