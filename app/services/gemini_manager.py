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
        """Initializes Gemini API configuration and loads prompt templates."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found! Please check your environment variables.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        self._load_prompts(prompts_path)

    def _load_prompts(self, prompts_path: str):
        """Loads prompt templates from a JSON file."""
        try:
            with open(prompts_path, "r", encoding="utf-8") as f:
                self.prompts = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompts_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Prompt file is not valid JSON: {prompts_path}")

    def generate_chat_response(self, prompt: str, character: str, is_time_travel: bool = False) -> str:
        """Formats the prompt based on roleplay type and requests a response from Gemini API."""
        if is_time_travel:
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
            return f"An error occurred: {str(e)}"

    def create_conversation_summary(self, messages: list, character_name: str) -> str:
        """Generates a summary of the conversation history using Gemini API."""
        if len(messages) < 2:
            return "Insufficient messages to generate a summary."

        conversation_text = ""
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                question = messages[i]["content"]
                answer = messages[i + 1]["content"]
                conversation_text += f"Question: {question}\nAnswer: {answer}\n\n"

        summary_prompt = self.prompts["summary_generation"].format(
            character_name=character_name,
            conversation_text=conversation_text
        )

        try:
            response = self.model.generate_content(summary_prompt)
            return response.text
        except Exception as e:
            return f"Failed to generate summary: {str(e)}"

    def analyze_conversation_style(self, messages: list) -> dict:
        """Analyzes user message keywords and suggests a matching historical character."""
        if len(messages) < 4:
            return None

        user_messages = [msg["content"].lower() for msg in messages if msg["role"] == "user"]
        all_text = " ".join(user_messages)

        suggestions = []

        philosophy_keywords = ["neden", "nasıl", "anlam", "düşünce", "felsefe", "hakikat", "bilgi", "akıl"]
        if any(keyword in all_text for keyword in philosophy_keywords):
            suggestions.extend([
                {"name": "Sokrates", "reason": "Your inquiry style mirrors Socrates' Socratic method."},
                {"name": "İbn Rüşd", "reason": "Your rational and logic-driven approach aligns with Averroes."},
                {"name": "Farabi", "reason": "Your search for knowledge echoes Al-Farabi's methodology."}
            ])

        war_keywords = ["savaş", "strateji", "ordu", "zafer", "mücadele", "liderlik"]
        if any(keyword in all_text for keyword in war_keywords):
            suggestions.extend([
                {"name": "Selahaddin Eyyubi", "reason": "Your interest in strategy and leadership matches Saladin."},
                {"name": "Napoléon Bonaparte", "reason": "Your focus on military strategy fits Napoleon."}
            ])

        art_keywords = ["sanat", "güzel", "estetik", "yaratıcı", "ilham", "şiir"]
        if any(keyword in all_text for keyword in art_keywords):
            suggestions.extend([
                {"name": "Michelangelo", "reason": "Your passion for art and creativity aligns with Michelangelo."},
                {"name": "Fuzuli", "reason": "Your aesthetic perspective resembles Fuzuli's poetry."}
            ])

        science_keywords = ["bilim", "keşif", "araştırma", "deney", "gözlem", "doğa"]
        if any(keyword in all_text for keyword in science_keywords):
            suggestions.extend([
                {"name": "Galileo Galilei", "reason": "Your scientific curiosity reflects Galileo's spirit."},
                {"name": "İbn Sina", "reason": "Your research drive aligns well with Avicenna."}
            ])

        return random.choice(suggestions) if suggestions else None

    def calculate_personality_match(self, user_scores: dict, characters_data: list) -> list:
        """Calculates trait similarities between user scores and historical characters, returning sorted matches."""
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