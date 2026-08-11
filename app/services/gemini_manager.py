"""
This module contains the GeminiManager class for managing Gemini API interactions
and business logic for personality tests and conversation style analysis.
"""

import os
import json
import random
import google.generativeai as genai

class GeminiManager:
    def __init__(self, model_name: str = "gemini-2.5-flash", prompts_path: str = "prompts/prompts.json"):
        """Gemini API yapılandırmasını ve promptları başlatır."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Promptları yükle
        self._load_prompts(prompts_path)

    def _load_prompts(self, prompts_path: str):
        """JSON dosyasından prompt kalıplarını okur."""
        try:
            with open(prompts_path, "r", encoding="utf-8") as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt dosyası bulunamadı: {prompts_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Prompt dosyası geçerli bir JSON değil: {prompts_path}")

    def generate_chat_response(self, prompt: str, character: str, is_time_travel: bool = False) -> str:
        """Karaktere veya zamanda yolculuk durumuna göre uygun prompt'u JSON'dan seçip formatlar ve API'den yanıt alır."""
        
        if is_time_travel:
            # JSON'dan kalıbı alıp değişkenleri dolduruyoruz
            ai_prompt = self.prompts["time_travel_roleplay"].format(
                character=character, 
                prompt=prompt
            )
        else:
            ai_prompt = self.prompts["standard_roleplay"].format(
                character=character, 
                prompt=prompt
            )
        
        try:
            response = self.model.generate_content(ai_prompt)
            return response.text
        except Exception as e:
            return f"Bir hata oluştu: {str(e)}"

    def create_conversation_summary(self, messages: list, character_name: str) -> str:
        """Sohbet geçmişini alır ve Gemini API kullanarak teknik bir özet çıkarır."""
        if len(messages) < 2:
            return "Özet oluşturmak için yeterli mesaj bulunmuyor."

        conversation_text = ""
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                question = messages[i]["content"]
                answer = messages[i + 1]["content"]
                conversation_text += f"Soru: {question}\nCevap: {answer}\n\n"

        # JSON'dan özet kalıbını alıp dolduruyoruz
        summary_prompt = self.prompts["summary_generation"].format(
            character_name=character_name,
            conversation_text=conversation_text
        )

        try:
            response = self.model.generate_content(summary_prompt)
            return response.text
        except Exception as e:
            return f"Özet oluştururken hata: {str(e)}"

    def analyze_conversation_style(self, messages: list) -> dict:
        """Kullanıcının konuşma tarzını analiz ederek ona bir karakter önerisi yapar."""
        if len(messages) < 4:
            return None

        user_messages = [msg["content"].lower() for msg in messages if msg["role"] == "user"]
        all_text = " ".join(user_messages)

        suggestions = []

        philosophy_keywords = ["neden", "nasıl", "anlam", "düşünce", "felsefe", "hakikat", "bilgi", "akıl"]
        if any(keyword in all_text for keyword in philosophy_keywords):
            suggestions.extend([
                {"name": "Sokrates", "reason": "Felsefi sorgulamalarınız Sokrates'in tarzına çok benziyor"},
                {"name": "İbn Rüşd", "reason": "Akıl ve mantık odaklı yaklaşımınız İbn Rüşd ile uyumlu"},
                {"name": "Farabi", "reason": "Bilgi arayışınız Farabi'nin yöntemleriyle örtüşüyor"}
            ])

        war_keywords = ["savaş", "strateji", "ordu", "zafer", "mücadele", "liderlik"]
        if any(keyword in all_text for keyword in war_keywords):
            suggestions.extend([
                {"name": "Selahaddin Eyyubi", "reason": "Strateji ve liderlik ilginiz Selahaddin'e uygun"},
                {"name": "Napoléon Bonaparte", "reason": "Askeri strateji merakınız Napoléon'la eşleşiyor"}
            ])

        art_keywords = ["sanat", "güzel", "estetik", "yaratıcı", "ilham", "şiir"]
        if any(keyword in all_text for keyword in art_keywords):
            suggestions.extend([
                {"name": "Michelangelo", "reason": "Sanat ve yaratıcılık ilginiz Michelangelo ile uyumlu"},
                {"name": "Fuzuli", "reason": "Estetik anlayışınız Fuzuli'nin şiirine yakın"}
            ])

        science_keywords = ["bilim", "keşif", "araştırma", "deney", "gözlem", "doğa"]
        if any(keyword in all_text for keyword in science_keywords):
            suggestions.extend([
                {"name": "Galileo Galilei", "reason": "Bilimsel merakınız Galileo'nun ruhunu yansıtıyor"},
                {"name": "İbn Sina", "reason": "Araştırma tutkunu İbn Sina'ya çok benziyor"}
            ])

        return random.choice(suggestions) if suggestions else None

    def calculate_personality_match(self, user_scores: dict, characters_data: list) -> list:
        """Kullanıcının kişilik puanlarını karakterlerle eşleştirip en yüksek yüzdelileri döndürür."""
        best_matches = []

        for character in characters_data:
            similarity_score = 0
            total_possible = 0

            for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
                user_score = user_scores.get(trait, 0)
                char_score = character["traits"][trait]

                diff = abs(user_score - char_score)
                similarity = 10 - diff

                similarity_score += similarity
                total_possible += 10

            match_percentage = (similarity_score / total_possible) * 100

            best_matches.append({
                "character": character,
                "percentage": match_percentage
            })

        return sorted(best_matches, key=lambda x: x["percentage"], reverse=True)