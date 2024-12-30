import streamlit as st
from llm_client import LlmClient
from assistant import Assistant
from chat_history import ChatHistory

class ChatApp:
    """Clase principal que orquesta el funcionamiento de la aplicación."""
    def __init__(self):
        self.client = LlmClient()
        self.assistant = Assistant(self.client)
        self.history = ChatHistory()
        self.flow_state = "INTRODUCTION"

        # Inicializar el estado de sesión y añadir la personalidad como mensaje de sistema oculto
        if "welcome_shown" not in st.session_state:
            # Estados posibles del flujo: INTRODUCTION, QUESTION_1, QUESTION_2, TAROT, FINISH
            st.session_state.welcome_shown = False
            st.session_state.messages = []
            # Añadir personalidad como mensaje de sistema y ocultarlo
            self.history.add_message("system", self.assistant.personality, hidden=True)

    def generate_laila_response(self, tone):
        """
        Genera un mensaje adaptado al tono de Laila.
        
        Args:
            tone (str): El tono deseado (e.g., 'amable', 'ofendida', 'neutral').
        
        Returns:
            None
        """
        tone_map = {
            "amable": "Laila responde con dulzura y comprensión.",
            "ofendida": "Laila se siente atacada y responde con desdén.",
            "neutral": "Laila responde de manera profesional y directa.",
        }
        # Cambiar el estado del flujo o añadir instrucciones específicas según el tono
        instruction = tone_map.get(tone, "Laila responde de manera estándar.")
        # Añadir mensaje al historial como un mensaje del sistema
        self.history.add_message("system", instruction, hidden=True)

    def is_disrespectful(self, user_response):
        """
        Verifica si la respuesta del usuario contiene una falta de respeto.
        
        Args:
            user_response (str): El mensaje del usuario a verificar.
        
        Returns:
            bool: True si el mensaje es irrespetuoso, False en caso contrario.
        """
        # Prepara el mensaje para el modelo de lenguaje
        disrespect_prompt = (
            "Recuerda, tú eres LAILA. Tu tarea ahora es verificar si este texto te está faltando al respeto:\n"
            f"Texto: '{user_response}'\n\n"
            "¿El texto te falta al respeto? Responde únicamente 'Sí' o 'No'."
        )
        # Usar el cliente para obtener la respuesta
        response = self.client.get_response([{"role": "system", "content": disrespect_prompt}])
        return response.strip().lower() == "sí"

    def run(self):
        """Ejecuta la aplicación de chat."""
        # Mostrar mensaje de bienvenida si es la primera interacción
        if not st.session_state.welcome_shown:
            welcome_message = self.assistant.generate_welcome_message()
            self.history.add_message("assistant", welcome_message)
            st.session_state.welcome_shown = True

        # Mostrar historial existente (solo mensajes visibles)
        self.history.display_messages()

        if self.flow_state == "INTRODUCTION":
            # Procesar entrada del usuario
            if prompt := st.chat_input("Escribe un mensaje..."):
                # Añadir y mostrar el mensaje del usuario
                self.history.add_message("user", content=prompt)
                with st.chat_message("user"):
                    st.markdown(prompt)

                # Verificar si el mensaje es irrespetuoso
                offended = False
                if self.is_disrespectful(prompt):
                    self.generate_laila_response("ofendida")
                    offended = True
                else:
                    self.generate_laila_response("amable")
                    offended = False

                # Procesar y mostrar la respuesta del asistente
                with st.chat_message("assistant"):
                    response = self.assistant.client.get_response(self.history.get_messages())
                    st.markdown(f"{self.flow_state} - {offended}:\n{response}")
                    self.history.add_message("assistant", content=response)
