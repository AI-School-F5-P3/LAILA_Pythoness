from utils.utils import get_env_key, WORLD, RED, RESET, THINKING, BRIGHT_GREEN, TURQUOISE, PASTEL_YELLOW, SPARKLES, RESET, RED, RAISED_HAND


import requests
import pycountry

class Assistant:
    """Clase que configura la personalidad y el flujo del asistente."""
    def __init__(self, client):
        try:
            # Cargar el prompt inicial de LAILA
            prompt_file = get_env_key("PROMPT_FILE")
            with open(prompt_file, "r", encoding="utf-8") as file:
                base_prompt = file.read()
        except FileNotFoundError:
            raise ValueError("Error: No se encontró el archivo de prompt.")
        
        self.personality = base_prompt
        self.client = client
        self.welcome_message = None
        
        # Registro de herramientas
        self.tools = {
            "detect_country": self.detect_country_tool,
            "generate_welcome_message": self.generate_welcome_message_tool
        }

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

    def use_tool(self, tool_name, *args):
        """Invoca una herramienta registrada."""
        if tool_name in self.tools:
            return self.tools[tool_name](*args)
        return f"Herramienta '{tool_name}' no encontrada."