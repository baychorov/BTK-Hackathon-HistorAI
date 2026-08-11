# app/core/config.py içerisine eklenecek/güncellenecek kısım

from dataclasses import dataclass, field

# ... (AppConfig, DatabaseConfig, AIConfig kısımları aynı kalacak)

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
    # ... (Singleton __new__ kısmı aynı)
    
    def _load_config(self):
        env = os.getenv("APP_ENV", "local")
        config_path = f"configs/config.{env}.toml"
        
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
                
            self.app = AppConfig(**data.get("app", {}))
            self.database = DatabaseConfig(**data.get("database", {}))
            self.ai = AIConfig(**data.get("ai", {}))
            self.export = ExportConfig(**data.get("export", {})) # Yeni eklenen satır
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Konfigürasyon dosyası bulunamadı: {config_path}")