import streamlit as st
import base64
from src.assistant import Assistant
from src.chat_history import ChatHistory
from src.flow_manager import FlowManager
from src.rag import RAG
from src.chat_history import ChatHistory
from src.utils.utils import get_env_key, THINKING, BRIGHT_GREEN, TURQUOISE, PASTEL_YELLOW, SPARKLES, RESET, RED, RAISED_HAND

class ChatApp:
    """Clase principal que orquesta el funcionamiento de la aplicación."""
    def __init__(self):        
        
        self.assistant = Assistant()
        self.history = ChatHistory()
        self.initialize_session_state()  # Llamado al inicio para asegurar estado inicializado

        # Asignar valores desde session_state al objeto
        self.asking = st.session_state.asking
        self.info = st.session_state.info

        # Configurar el flujo del paso
        self.flow_manager = FlowManager(st.session_state.step, max_steps=8)
        self.step = self.flow_manager.current_step + 1

        # Cargar imágenes
        self.laila_avatar = self.load_image_as_base64("frontend/static/img/laila_avatar.webp")
        self.user_avatar = self.load_image_as_base64("frontend/static/img/user.png")

        # Definir los estados y acciones del flujo
        self.state_actions = {
            "INTRODUCTION": self.handle_response_from_introduction,
            "QUESTION_1": self.handle_response_from_question_1,
            "QUESTION_2": self.handle_response_from_question_2,
            "PREPARE": self.handle_response_from_prepare,
            "TAROT": self.handle_response_from_tarot,
            "FINISH": self.handle_final_response
        }

        self.rag = RAG()

    def initialize_session_state(self):
        """Inicializar todas las claves del estado de sesión en un solo lugar, incluyendo las tools."""
        defaults = {
            "app_initialized": False,
            "asking": None,
            "info": None,
            "step": 0,
            "flow_state": "INTRODUCTION",
            "welcome_shown": False,
            "messages": [],
            "disabled": False,
            "tools": {
                "detect_country": self.assistant.detect_country_tool,
                "generate_welcome_message": self.assistant.generate_welcome_message_tool,
                "is_comprensible_message": self.assistant.is_comprensible_message_tool,
                "laila_tarot_reading": self.assistant.laila_tarot_reading_tool
            }
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


    def load_image_as_base64(self, path):
        """Carga una imagen y la convierte a base64."""
        with open(path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"

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
        print(f"\n{PASTEL_YELLOW}🔮 Interacción:{RESET} {self.step} {PASTEL_YELLOW}Paso activo:{RESET} QUESTION_1")
        st.session_state.asking = self.history.get_messages()[-1]["content"]
        self.asking = st.session_state.asking
        print(f"\n{PASTEL_YELLOW}🦉 El usuario dijo(self.asking):{RESET} {self.asking}")
               
        self.advance_local_step()
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
        # #tirada
        # tirada = self.assistant.use_tool("laila_tarot_reading", self.asking, self.info)
        # print(f"\n{TURQUOISE}✨ RESULTADO DE LA TIRADA:{RESET}\n{tirada}")

        
        # self.history.add_message("user", content=get_env_key('PROMPT_TAROT'), hidden=True)
        # self.laila_response("solemne")

        tirada = self.assistant.use_tool("laila_tarot_reading", self.asking, self.info)
        self.history.add_message("assistant", content=tirada, hidden=True)
        self.laila_reading(tirada)

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
    
    def laila_reading(self, text):
        st.chat_message("assistant",  avatar=self.laila_avatar).markdown(f"{text}")
        self.history.add_message("assistant", content=text, hidden=False)

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

    def disable(self,value):
        st.session_state.disabled = value

    # def run(self):
    #     """Ejecuta la aplicación de chat."""
    #     if not st.session_state.app_initialized:
    #         st.session_state.app_initialized = True
    #         welcome_message = self.assistant.use_tool("generate_welcome_message")
    #         self.history.add_message("assistant", welcome_message)
    #         st.session_state.welcome_shown = True

    #     self.history.display_messages()
        
    #     # Inicializar el estado del botón deshabilitado
    #     if "disabled" not in st.session_state:
    #         self.disable(False)
        
    #     # Si ya terminó el flujo, deshabilitar la entrada
    #     if not self.flow_manager.can_continue():
    #         self.disable(True)

    #     prompt = st.chat_input("Escribe un mensaje...", disabled=st.session_state.disabled)
        
    #     if prompt and not st.session_state.disabled:            
    #         self.history.add_message("user", content=prompt)            
    #         st.chat_message("user", avatar=self.user_avatar).markdown(prompt)
        
    #     if self.flow_manager.can_continue():
    #         comprensible_message = self.assistant.use_tool("is_comprensible_message", self.asking)
    #         if comprensible_message:
    #             if not self.is_disrespectful(prompt):
    #                 current_state = st.session_state.flow_state
    #                 if current_state in self.state_actions:
    #                     self.state_actions[current_state]()
    #                 else:
    #                     st.error(f"Estado desconocido: {current_state}")
    #             else:
    #                 self.history.add_message("user", content="Se te ha ofendido gravemente", hidden=True)
    #                 self.history.add_message("user", content="Te despides dramatica y teatralmente y cierras la sesión hasta que reconsidere su lenguaje.", hidden=True)
    #                 self.laila_response("ofendida y teatral")
    #                 with st.container(key="ofended"):
    #                     st.write("🔮 Por favor, utiliza un lenguaje respetuoso. ")
    #         else:
    #             self.history.add_message("user", content=get_env_key('PROMPT_CHAT'), hidden=True)
    #             self.laila_response("excéntrica y teatral")
    #     else:
    #             print(f"\n{PASTEL_YELLOW}{RAISED_HAND} Finaliza el flujo{RESET}")
    #             self.flow_manager.finish()
    #             st.session_state.disabled = True
    #             self.history.add_message("user", content=get_env_key('PROMPT_CHAT'), hidden=True)
    #             self.laila_response("excéntrica y teatral")

    def run(self):
        """Ejecuta la aplicación de chat con control para evitar ejecución doble."""
        # Control estricto de inicialización
        if not st.session_state.get("app_initialized", False):
            st.session_state.app_initialized = True
            welcome_message = self.assistant.use_tool("generate_welcome_message")
            self.history.add_message("assistant", welcome_message)
            st.session_state.welcome_shown = True

        # Evitar doble ejecución con control explícito de reinicio
        if st.session_state.get("executing", False):
            return
        st.session_state.executing = True

        self.history.display_messages()

        # Deshabilitar entrada si el flujo terminó
        st.session_state.disabled = not self.flow_manager.can_continue()
        
        # Campo de entrada deshabilitado
        prompt = st.chat_input("Escribe un mensaje...", disabled=st.session_state.disabled)
        
        if prompt and not st.session_state.disabled:
            self.history.add_message("user", content=prompt)            
            st.chat_message("user", avatar=self.user_avatar).markdown(prompt)
            
            comprensible_message = self.assistant.use_tool("is_comprensible_message", self.asking)
            if comprensible_message:
                if not self.is_disrespectful(prompt):
                    current_state = st.session_state.flow_state
                    if current_state in self.state_actions:
                        self.state_actions[current_state]()
                    else:
                        st.error(f"Estado desconocido: {current_state}")
                else:
                    self.history.add_message("user", content="Se te ha ofendido gravemente", hidden=True)
                    self.history.add_message("user", content="Te despides dramaticamente y cierras la sesión.", hidden=True)
                    self.laila_response("ofendida y teatral")
            else:
                self.history.add_message("user", content=get_env_key('PROMPT_CHAT'), hidden=True)
                self.laila_response("excéntrica y teatral")

        # Finalizar si no se puede continuar
        if not self.flow_manager.can_continue():
            st.session_state.disabled = True
            self.history.add_message("user", content=get_env_key('PROMPT_CHAT'), hidden=True)
            self.laila_response("excéntrica y teatral")
            
        # Reset para permitir futuras ejecuciones controladas
        st.session_state.executing = False

# Instanciar y ejecutar la aplicación
if __name__ == "__main__":
    app = ChatApp()
    app.run()