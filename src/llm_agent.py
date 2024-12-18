import os
from langchain_groq import ChatGroq

class LLMAgent:
    def __init__(self):
        """
        Inicializa el agente LLM usando Groq API y el modelo especificado.
        """
        groq_api_key = os.environ.get('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("La clave GROQ_API_KEY no está definida en las variables de entorno.")
        
        model = 'llama-3.3-70b-versatile'
        self.chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

    def generate_response(self, messages):
        """
        Genera una respuesta del modelo Groq usando el historial de mensajes.
        """
        try:
            # LangChain espera una lista de mensajes con formato correcto
            response = self.chat.invoke(messages)
            return response.content  # Devuelve solo el contenido del mensaje
        except Exception as e:
            return f"Error en la respuesta del LLM: {str(e)}"

# Prueba del funcionamiento de LLM
if __name__ == "__main__":
    # Mensaje de prueba para verificar la conexión
    print("Probando el agente LLM con Groq...\n")
    
    agent = LLMAgent()

    # Mensajes simulados para la conversación
    test_messages = [
        {"role": "system", "content": "Eres un asistente que responde con claridad y precisión."},
        {"role": "user", "content": "¿Cuál es la capital de Francia?"}
    ]
    
    # Generar respuesta
    response = agent.generate_response(test_messages)
    print("Respuesta del modelo:\n")
    print(response)
