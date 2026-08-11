"""
This module contains the DatabaseService class for managing SQLite database operations.
The DatabaseService class provides methods to initialize the database, create and manage conversations and messages.
"""

# app/database/database.py

import sqlite3
import os

class DatabaseService:
    def __init__(self, db_path: str = "database/historai.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self.initialize_database()

    def _ensure_db_directory(self):
        """Veritabanı klasörünün var olduğundan emin olur."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def _get_connection(self):
        """SQLite bağlantısı döndürür."""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def initialize_database(self):
        """Uygulama ilk başladığında tabloları ve güncellemeleri kurar."""
        with self._get_connection() as conn:
            c = conn.cursor()
            
            # Yeni tablo yapısı: conversations
            c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          character TEXT, 
                          title TEXT,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          is_pinned BOOLEAN DEFAULT 0,
                          conversation_type TEXT DEFAULT 'normal',
                          session_id TEXT)''')

            # Yeni tablo yapısı: messages
            c.execute('''CREATE TABLE IF NOT EXISTS messages 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          conversation_id INTEGER, 
                          question TEXT, 
                          answer TEXT, 
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          session_id TEXT,
                          FOREIGN KEY (conversation_id) REFERENCES conversations (id))''')
            
            # Eski tablodan (chats) geçiş kontrolü (Geriye dönük uyumluluk)
            c.execute("PRAGMA table_info(chats)")
            old_table_exists = c.fetchall()
            if old_table_exists:
                c.execute("SELECT character, question, answer FROM chats")
                old_chats = c.fetchall()
                for char, ques, ans in old_chats:
                    c.execute("INSERT INTO conversations (character, title, session_id) VALUES (?, ?, ?)",
                              (char, ques[:50] + "..." if len(ques) > 50 else ques, 'legacy'))
                    conv_id = c.lastrowid
                    c.execute("INSERT INTO messages (conversation_id, question, answer, session_id) VALUES (?, ?, ?, ?)",
                              (conv_id, ques, ans, 'legacy'))
                c.execute("DROP TABLE chats")

            # Eğer tablolar zaten varsa, eksik kolonları eklemeyi dene
            try:
                c.execute("ALTER TABLE conversations ADD COLUMN session_id TEXT")
                c.execute("UPDATE conversations SET session_id = 'legacy' WHERE session_id IS NULL")
            except sqlite3.OperationalError:
                pass  # Kolon zaten mevcut
                
            try:
                c.execute("ALTER TABLE messages ADD COLUMN session_id TEXT")
                c.execute("UPDATE messages SET session_id = 'legacy' WHERE session_id IS NULL")
            except sqlite3.OperationalError:
                pass  # Kolon zaten mevcut

            conn.commit()

    # --- CRUD OPERASYONLARI ---

    def create_conversation(self, character: str, title: str, conv_type: str, session_id: str) -> int:
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO conversations (character, title, conversation_type, session_id) VALUES (?, ?, ?, ?)",
                (character, title, conv_type, session_id)
            )
            conn.commit()
            return c.lastrowid

    def update_conversation_title(self, conv_id: int, title: str, session_id: str):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE conversations SET title = ? WHERE id = ? AND session_id = ?", 
                      (title, conv_id, session_id))
            conn.commit()
            
    def toggle_pin_status(self, conv_id: int, is_pinned: bool, session_id: str):
        new_status = 1 if is_pinned else 0
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE conversations SET is_pinned = ? WHERE id = ? AND session_id = ?",
                      (new_status, conv_id, session_id))
            conn.commit()

    def get_conversations(self, session_id: str, filter_char: str = None):
        with self._get_connection() as conn:
            c = conn.cursor()
            if filter_char:
                c.execute("""SELECT id, character, title, is_pinned, conversation_type 
                             FROM conversations 
                             WHERE character LIKE ? AND session_id = ? 
                             ORDER BY is_pinned DESC, created_at DESC""", 
                          ('%' + filter_char + '%', session_id))
            else:
                c.execute("""SELECT id, character, title, is_pinned, conversation_type 
                             FROM conversations 
                             WHERE session_id = ? 
                             ORDER BY is_pinned DESC, created_at DESC""", 
                          (session_id,))
            return c.fetchall()

    def delete_conversation(self, conv_id: int, session_id: str):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM messages WHERE conversation_id = ? AND session_id = ?", (conv_id, session_id))
            c.execute("DELETE FROM conversations WHERE id = ? AND session_id = ?", (conv_id, session_id))
            conn.commit()

    def delete_all_history(self, session_id: str):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            c.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()

    def add_message(self, conv_id: int, question: str, answer: str, session_id: str):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO messages (conversation_id, question, answer, session_id) VALUES (?, ?, ?, ?)",
                (conv_id, question, answer, session_id)
            )
            conn.commit()

    def get_messages(self, conv_id: int, session_id: str):
        with self._get_connection() as conn:
            c = conn.cursor()
            c.execute(
                "SELECT question, answer FROM messages WHERE conversation_id = ? AND session_id = ? ORDER BY created_at",
                (conv_id, session_id)
            )
            return c.fetchall()
            
    def get_conversation_info(self, conv_id: int, session_id: str):
         with self._get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT character, title FROM conversations WHERE id = ? AND session_id = ?",
                      (conv_id, session_id))
            return c.fetchone()