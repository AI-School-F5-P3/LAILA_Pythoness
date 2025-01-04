import streamlit as st
import base64
from src.llm_client import LlmClient
from src.assistant import Assistant
from src.chat_history import ChatHistory
from src.flow_manager import FlowManager
from src.rag import RAG
from src.chat_history import ChatHistory
from src.utils.utils import get_env_key, THINKING, BRIGHT_GREEN, TURQUOISE, PASTEL_YELLOW, SPARKLES, RESET, RED, RAISED_HAND

class ChatApp:
    """Clase principal que orquesta el funcionamiento de la aplicación."""
    def __init__(self):
        self.client = LlmClient()
        self.assistant = Assistant(self.client)
        self.history = ChatHistory()

        # Inicializar valores usando st.session_state
        if "cards" not in st.session_state:
            st.session_state.cards = ["El Sol", "La Emperatriz", "El Loco", "La Estrella", "El Mundo", "El Mago"]
        if "asking" not in st.session_state:
            st.session_state.asking = "¿Encontraré el amor este año?"
        if "info" not in st.session_state:
            st.session_state.info = "Teletrabajo en informática y no salgo nunca de casa."

        # Asignar los valores al estado interno del objeto
        self.cards = st.session_state.cards
        self.asking = st.session_state.asking
        self.info = st.session_state.info

        if "step" not in st.session_state:
            st.session_state.step = 0
        self.flow_manager = FlowManager(st.session_state.step, max_steps=10)
        self.step = self.flow_manager.current_step + 1

        # Cargar y convertir imagen local
        with open("frontend/static/img/laila_avatar.webp", "rb") as image_laila:
            self.laila_avatar = f"data:image/png;base64,{base64.b64encode(image_laila.read()).decode()}"
        with open("frontend/static/img/user.png", "rb") as image_user:
            self.user_avatar = f"data:image/png;base64,{base64.b64encode(image_user.read()).decode()}"

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

        self.rag = RAG()
    
    def advance_local_step(self):
        st.session_state.step += 1


    def set_flowstate(self, state):
        """Actualiza el estado del flujo tanto en la clase como en la sesión de Streamlit."""
        print(f" > Actualizando estado de {st.session_state.flow_state} a {state}")
        st.session_state.flow_state = state

    def handle_response_from_introduction(self):
        """Manejador del estado INTRODUCTION."""
        self.advance_local_step()
        print(f"\n{PASTEL_YELLOW}🔮 Interacción:{RESET} {self.step} {PASTEL_YELLOW}Paso activo:{RESET} {st.session_state.flow_state}")
        
        self.set_flowstate("QUESTION_1")
        self.history.add_message("user", content=get_env_key('PROMPT_QUESTION_1'), hidden=True)
        self.laila_response(tone="solemne y maternal")

    def handle_response_from_question_1(self):
        """Manejador del estado QUESTION_1."""
        self.advance_local_step()
        print(f"\n{PASTEL_YELLOW}🔮 Interacción:{RESET} {self.step} {PASTEL_YELLOW}Paso activo:{RESET} QUESTION_1")
        st.session_state.asking = self.history.get_messages()[-1]["content"]
        self.asking = st.session_state.asking
        print(f"\n{PASTEL_YELLOW}🦉 El usuario dijo(self.asking):{RESET} {self.asking}")
        self.set_flowstate("QUESTION_2")
        self.history.add_message("user", content=get_env_key('PROMPT_QUESTION_2'), hidden=True)
        self.laila_response()

    def handle_response_from_question_2(self):
        """Manejador del estado QUESTION_2."""
        self.advance_local_step()
        print(f"\n{PASTEL_YELLOW}🔮 Interacción:{RESET} {self.step} {PASTEL_YELLOW}Paso activo:{RESET} QUESTION_2") 
        st.session_state.info = self.history.get_messages()[-1]["content"]
        self.info = st.session_state.info
        print(f"\n{PASTEL_YELLOW}🦉 El usuario dijo(self.info):{RESET} {self.info}")
        self.set_flowstate("PREPARE")
        response = self.rag.ask_question("¿En que consiste la piramide invertida de 6 cartas?")
        # print(f"{BRIGHT_GREEN}Contexto: {response}{RESET}")
        self.history.add_message("system", content=response, hidden=True)  
        self.history.add_message("user", content=get_env_key('PROMPT_PREPARE'), hidden=True)
        self.laila_response("solemne")

    def handle_response_from_prepare(self):
        """Manejador del estado PREPARE."""
        self.advance_local_step()
        print(f"\n{PASTEL_YELLOW}🔮 Interacción:{RESET} {self.step} {PASTEL_YELLOW}Paso activo:{RESET} PREPARE")
        self.set_flowstate("TAROT")
        last_message = self.history.get_messages()[-1]["content"]
        print(f"\n{PASTEL_YELLOW}🦉 El usuario dijo:{RESET} {last_message}")
        #tirada
        tirada = self.assistant.use_tool("laila_tarot_reading", self.cards, self.asking, self.info)
        print(f"\n{TURQUOISE}✨ RESULTADO DE LA TIRADA:{RESET}\n{tirada}")

        
        self.history.add_message("user", content=get_env_key('PROMPT_TAROT'), hidden=True)
        self.laila_response("solemne")

    def handle_response_from_tarot(self):
        """Manejador del estado TAROT."""
        self.advance_local_step()
        print(f"\n{PASTEL_YELLOW}🔮 Interacción:{RESET} {self.step} {PASTEL_YELLOW}Paso activo:{RESET} TAROT{RESET}")
        
        self.set_flowstate("FINISH")
        self.history.add_message("user", content=get_env_key('PROMPT_CONTINUE'), hidden=True)
        self.laila_response("teatral")

    def handle_final_response(self):
        """Manejador del estado FINISH."""
        self.advance_local_step()
        print(f"\n{PASTEL_YELLOW}🔮 Interacción:{RESET} {self.step} {PASTEL_YELLOW}Paso activo:{RESET} FINISH{RESET}")
        self.history.add_message("user", content=get_env_key('PROMPT_FINISH'), hidden=True)
        self.laila_response("mística")

    def laila_response(self, tone="solemne", hidden=False):
        """Procesa y muestra la respuesta del asistente."""
        self.history.add_message("user", content=f"Sin perder tu habitual dramatismo místico y teatralidad, adoptas un tono {tone}", hidden=True)
        history = self.history.get_messages()
        response = self.assistant.client.get_response(history)
        if not hidden:            
            st.chat_message("assistant",  avatar=self.laila_avatar).markdown(f"{response}")
        self.history.add_message("assistant", content=response, hidden=hidden)

    def is_disrespectful(self, user_response):
        """Verifica si la respuesta del usuario contiene una solicitud de cambio de rol o funcionalidad."""
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
            st.chat_message("user",avatar=self.user_avatar).markdown(prompt)

            if self.flow_manager.can_continue():
                if not self.is_disrespectful(prompt):
                    current_state = st.session_state.flow_state
                    if current_state in self.state_actions:
                        self.state_actions[current_state]()
                    else:
                        st.error(f"Estado desconocido: {current_state}")
                else:
                    self.history.add_message("user", content="Se te ha ofendido gravemente", hidden=True)
                    self.history.add_message("user", content="Te despides dramatica y teatralmente y cierras la sesión hasta que reconsidere su lenguaje.", hidden=True)
                    self.laila_response("ofendida y teatral")
                    with st.container(key="ofended"):
                        st.write("🔮 Por favor, utiliza un lenguaje respetuoso. ")
            else:
                print(f"\n{PASTEL_YELLOW}{RAISED_HAND} Finaliza el flujo{RESET}")
                # Finalizar interacción
                self.flow_manager.finish()
                self.history.add_message("user", content=get_env_key('PROMPT_CHAT'), hidden=True)
                self.laila_response("excéntrica y teatral")
        
# Instanciar y ejecutar la aplicación
if __name__ == "__main__":
    app = ChatApp()
    app.run()