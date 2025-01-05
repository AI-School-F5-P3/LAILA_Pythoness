import requests
import pycountry
import streamlit as st
from src.llm_client import LlmClient
from src.utils.utils import get_env_key, WORLD, RED, RESET, THINKING, BRIGHT_GREEN, TURQUOISE, PASTEL_YELLOW, SPARKLES, RESET, RED, RAISED_HAND
from src.tarot_reader import TarotReader

class Assistant:
    """Clase que configura la personalidad y el flujo del asistente."""
    def __init__(self):
        try:
            # Cargar el prompt inicial de LAILA
            prompt_file = get_env_key("PROMPT_FILE")
            with open(prompt_file, "r", encoding="utf-8") as file:
                base_prompt = file.read()
        except FileNotFoundError:
            raise ValueError("Error: No se encontró el archivo de prompt.")
        
        self.personality = base_prompt
        self.client = LlmClient()
        self.welcome_message = None
        
        # Registro de herramientas
        if "tools" not in st.session_state:
            st.session_state.tools = {
                "detect_country": self.detect_country_tool,
                "generate_welcome_message": self.generate_welcome_message_tool,
                "is_comprensible_message": self.is_comprensible_message_tool,
                "laila_tarot_reading": self.laila_tarot_reading_tool
            }

        self.tools = st.session_state.tools


    def detect_country_tool(self):
        """Detecta el país y el idioma del usuario utilizando su IP."""
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            if response.status_code == 200:
                country = data.get("country", "Unknown")
                country_code = data.get("countryCode", "XX")
                language = self.get_language_from_country(country_code)
                return country, country_code, language
            else:
                return "Unknown", "XX", "en"
        except Exception as e:
            return "Error detectando país", "XX", "en"

    def get_language_from_country(self, country_code):
        """Obtiene el idioma principal de un país usando pycountry."""
        try:
            country = pycountry.countries.get(alpha_2=country_code)
            if not country:
                return "en"
            # Usa pycountry_languages para obtener el idioma
            languages = list(pycountry.languages)
            for lang in languages:
                if hasattr(lang, 'alpha_2') and lang.alpha_2 == country.alpha_2.lower():
                    return lang.alpha_2
            return "en"  # Predeterminado a inglés si no se encuentra
        except Exception:
            return "en"

    def generate_welcome_message_tool(self):
        """Genera un mensaje de bienvenida traducido al idioma del usuario."""
        country, country_code, language = self.detect_country_tool()
        print(f"{PASTEL_YELLOW}{WORLD} Pais: {country}, Idioma: {country_code}{RESET}")

        prompt = get_env_key('PROMPT_INTRO')
        messages_with_context = [
            {"role": "system", "content": self.personality},
            {"role": "user", "content": f"{prompt} Genera el mensaje en {language}."}
        ]
        return self.client.get_response(messages_with_context)

    def laila_tarot_reading_tool(self,asking, info):
        return TarotReader().reading(asking, info)

    # Verificacion de mensajes de chat
    def is_comprensible_message_tool(self, user_response):
        """Verifica si la respuesta del usuario contiene se entiende."""
        comprensible_prompt = (
            f"El usuario ha dicho: '{user_response}'\n"
            "¿Se entiende esta respuesta? Responde únicamente 'Sí' o 'No'."
        )
        response = self.client.get_response([
            {"role": "user", "content": comprensible_prompt}
        ])

        response =  'sí' in response.strip().lower()

        print(f"\n{PASTEL_YELLOW}{THINKING} Se entiende la respuesta?{RESET} {response}")  # Imprime la respuesta completa del LLM para depuración

        return response

    def use_tool(self, tool_name, *args):
        """Invoca una herramienta registrada desde st.session_state con control de ejecución."""
        if tool_name in st.session_state.tools:
            return st.session_state.tools[tool_name](*args)
        return f"Herramienta '{tool_name}' no encontrada."
