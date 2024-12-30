import streamlit as st
from llm_client import LlmClient
from assistant import Assistant
from chat_history import ChatHistory
from utils.utils import get_env_key

class ChatApp:
    """Clase principal que orquesta el funcionamiento de la aplicación."""
    def __init__(self):
        self.client = LlmClient()
        self.assistant = Assistant(self.client)
        self.history = ChatHistory()

        # Inicializar estado de sesión
        if "flow_state" not in st.session_state:
            st.session_state.flow_state = "INTRODUCTION"

        if "welcome_shown" not in st.session_state:
            st.session_state.welcome_shown = False
            st.session_state.messages = []

        # Mapear estados a sus funciones
        self.state_actions = {
            "INTRODUCTION": self.handle_response_from_introduction,
            "QUESTION_1": self.handle_response_from_question_1,
            "QUESTION_2": self.handle_response_from_question_2,
            "PREPARE": self.handle_response_from_prepare,
            "TAROT": self.handle_response_from_tarot,
            "FINISH": self.handle_final_response
        }

    def set_flowstate(self, state):
        """Actualiza el estado del flujo tanto en la clase como en la sesión de Streamlit."""
        print(f"Actualizando estado de {st.session_state.flow_state} a {state}")
        st.session_state.flow_state = state

    def handle_response_from_introduction(self):
        """Manejador del estado de introducción."""
        print("Ejecutando handle_response_from_introduction")
        self.set_flowstate("QUESTION_1")
        self.history.add_message("user", content=get_env_key('PROMPT_QUESTION_1'), hidden=True)
        self.laila_response("QUESTION_1", self.history.get_messages())

    def handle_response_from_question_1(self):
        """Manejador del estado QUESTION_1."""
        print("Ejecutando handle_response_from_question_1")
        self.set_flowstate("QUESTION_2")
        self.history.add_message("user", content=get_env_key('PROMPT_QUESTION_2'), hidden=True)
        self.laila_response("QUESTION_2", self.history.get_messages())

    def handle_response_from_question_2(self):
        """Manejador del estado QUESTION_2."""
        print("Ejecutando handle_response_from_question_2")
        self.set_flowstate("PREPARE")
        self.history.add_message("user", content=get_env_key('PROMPT_PREPARE'), hidden=True)
        self.laila_response("PREPARE", self.history.get_messages())

    def handle_response_from_prepare(self):
        """Manejador del estado PREPARE."""
        print("Ejecutando handle_response_from_prepare")
        self.set_flowstate("TAROT")
        self.history.add_message("user", content=get_env_key('PROMPT_TAROT'), hidden=True)
        self.laila_response("TAROT", self.history.get_messages())

    def handle_response_from_tarot(self):
        """Manejador del estado TAROT."""
        print("Ejecutando handle_response_from_tarot")
        self.set_flowstate("FINISH")
        self.history.add_message("user", content=get_env_key('PROMPT_CONTINUE'), hidden=True)
        self.laila_response("CONTINUE", self.history.get_messages())

    def handle_final_response(self):
        """Manejador del estado FINISH."""
        print("Ejecutando handle_response_from_finish")
        self.history.add_message("user", content=get_env_key('PROMPT_FINISH'), hidden=True)
        self.laila_response("FINISH", self.history.get_messages())

    def laila_response(self, flow, history, hidden=False):
        """Procesa y muestra la respuesta del asistente."""
        response = self.assistant.client.get_response(history)
        if not hidden:
            st.chat_message("assistant").markdown(f"{response}")
        self.history.add_message("assistant", content=response, hidden=hidden)

    def is_disrespectful(self, user_response):
        """Verifica si la respuesta del usuario contiene una falta de respeto."""
        disrespect_prompt = (
            f"El usuario ha dicho: '{user_response}'\n"
            "Te está faltando al respeto? Responde únicamente 'Sí' o 'No'."
        )
        response = self.assistant.client.get_response([
            {"role": "user", "content": disrespect_prompt}
        ])
        return 'sí' in response.strip().lower()

    def run(self):
        """Ejecuta la aplicación de chat."""
        if not st.session_state.welcome_shown:
            # welcome_message = self.assistant.generate_welcome_message()
            welcome_message = self.assistant.use_tool("generate_welcome_message")
            self.history.add_message("assistant", welcome_message)
            st.session_state.welcome_shown = True

        self.history.display_messages()

        if prompt := st.chat_input("Escribe un mensaje..."):
            self.history.add_message("user", content=prompt)
            st.chat_message("user").markdown(prompt)

            if not self.is_disrespectful(prompt):
                current_state = st.session_state.flow_state
                if current_state in self.state_actions:
                    self.state_actions[current_state]()
                else:
                    st.error(f"Estado desconocido: {current_state}")
            else:
                self.history.add_message("user", content="Se te ha ofendido gravemente", hidden=True)
                self.history.add_message("user", content="Te despides dramatica y teatralmente y cierras la sesión hasta que reconsidere su lenguaje.", hidden=True)
                self.laila_response("RESPUESTA", self.history.get_messages()) 
                st.write("Por favor, utiliza un lenguaje respetuoso.")

# Instanciar y ejecutar la aplicación
if __name__ == "__main__":
    app = ChatApp()
    app.run()
