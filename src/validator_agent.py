from llm_agent import LLMAgent

pregunta_valida=""" 
"""
class ValidatorAgent:
    def __init__(self):
        self.rules = {
            1: "Debes entender lo que el usuario dice.",
            2: "La respuesta debe profundizar en detalles adicionales o aspectos ocultos.",
            3: "La respuesta debe confirmar si estás preparado para continuar con la tirada."
        }
        self.llm_agent = LLMAgent()

    def validate(self, interaction_number, user_response):
        """
        Valida la respuesta del usuario según las reglas predefinidas.
        """
        expected_rule = self.rules.get(interaction_number, "")
        validation_prompt = (
            "Eres un asistente que valida respuestas del usuario. "
            "La regla es la siguiente:\n"
            f"Regla: {expected_rule}\n"
            f"Respuesta del usuario: {user_response}\n"
            "¿La respuesta cumple con la regla? Responde 'Sí' o 'No'."
        )

        # Validación de reglas
        validation_result = self.llm_agent.generate_response([
            {"role": "user", "content": validation_prompt}
        ])
        return "Sí" in validation_result

    def is_valid_tarot_question(self, user_response):
        """
        Verifica si la entrada es una pregunta válida para el tarot.
        """
        tarot_validation_prompt = (
            f"{pregunta_valida}"
            "Tu tarea es valida si la siguiente pregunta "
            "es adecuada para una lectura de tarot.\n\n"
            f"Pregunta: {user_response}\n\n"
            "Responde únicamente 'Sí' si la pregunta es válida para el tarot, "
            "o 'No' si no lo es."
        )

        # Llamada al LLM para verificar la validez de la pregunta
        validation_result = self.llm_agent.generate_response([
            {"role": "user", "content": tarot_validation_prompt}
        ])
        return "Sí" in validation_result

    def is_disrespectful(self, user_response):
        """
        Verifica si la respuesta del usuario contiene una falta de respeto.
        """
        disrespect_prompt = (
            "Eres LAILA. Tu tarea es analizar la siguiente entrada:\n"
            f"Entrada del usuario: '{user_response}'\n\n"
            "¿La entrada contiene alguna falta de respeto, insulto o lenguaje ofensivo? "
            "Responde únicamente 'Sí' o 'No'."
        )
        
        # Llamada al LLM para verificar si es irrespetuoso
        validation_result = self.llm_agent.generate_response([
            {"role": "user", "content": disrespect_prompt}
        ])
        return "Sí" in validation_result

# Prueba del ValidatorAgent
if __name__ == "__main__":
    agent = ValidatorAgent()

    # Ejemplo de pruebas
    print("Validando pregunta de tarot:")
    print(agent.is_valid_tarot_question("¿Qué debo tener en cuenta para tomar la mejor decisión?"))  # Espera 'Sí'

    print("Validando falta de respeto:")
    print(agent.is_disrespectful("Eres una basura"))  # Espera 'Sí'

    print("Validando claridad de respuesta:")
    print(agent.validate(1, "J me quiere?"))  # Espera 'Sí'
