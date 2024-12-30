from langchain_groq import ChatGroq
from openai import OpenAI
from utils.utils import get_env_key, THINKING, TURQUOISE, PASTEL_YELLOW, SPARKLES, RESET, RED
from llm_agent import LLMAgent  # Importamos la clase del archivo proporcionado

class TarotFlow:
    def __init__(self, llm_model="llama-3.3-70b-versatile"):
        """
        Inicializa el flujo de tarot con un agente LLM.
        """
        self.state = "INTRODUCTION"  # Estados posibles: INTRODUCTION, QUESTION_1, tirada, cierre, fin
        self.messages = []  # Historial de mensajes para el contexto
        self.agent = LLMAgent(self.messages, llm_model)

    def handle_state(self, user_input=None):
        """
        Maneja el flujo de interacción según el estado actual.
        """
        if self.state == "INTRODUCTION":
            try:
                # Cargar el prompt inicial de LAILA
                prompt_file = get_env_key("PROMPT_FILE")
                with open(prompt_file, "r", encoding="utf-8") as file:
                    base_prompt = file.read()
            except FileNotFoundError:
                print(f"{RED}Error: No se encontró el archivo de prompt.{RESET}")
                return
            intro = get_env_key('PROMPT_INTRO')
            self.agent.add_message("system", base_prompt)
            response = self.agent.generate_response('assistant', intro)
            self.state = "QUESTION_1"
            return response

        elif self.state == "QUESTION_1":
            if not user_input:
                return "Por favor, formula tu pregunta para que las cartas puedan guiarte." 
            self.agent.add_message("user", user_input)          
            # self.agent.add_message('assistant', get_env_key('PROMPT_QUESTION_1')) 
            prompt = self.agent.generate_response('assistant', "respondes solemnemente con la personalidad de LAILA. No uses mas de 100 palabras para tu respuessta.")
            # self.state = "tirada"
            return self.agent.generate_response()

        elif self.state == "tirada":
            prompt = (
                "Contesta cariñosamente."
            )
            self.agent.add_message("system", prompt)
            response = self.agent.generate_response("assistant", prompt)
            self.state = "cierre"
            return response

        elif self.state == "cierre":
            prompt = (
                "Lo que está dicho, está sellado. ¿Deseas conversar más sobre esta tirada, "
                "o dejamos que las cartas guarden sus secretos por ahora?"
            )
            self.agent.add_message("system", prompt)
            self.state = "fin"
            return prompt

        elif self.state == "fin":
            return "Gracias por confiar en las cartas. Hasta la próxima."

# Ejemplo de uso
if __name__ == "__main__":
    flow = TarotFlow()
    print(f"\n{TURQUOISE}{SPARKLES} Paso: {SPARKLES} {flow.state} {SPARKLES} {flow.handle_state()}{RESET}") # Inicia el flujo

    while True:
        user_input = input("Tu: ")
        response = flow.handle_state(user_input)
        print(f"\n{TURQUOISE}{SPARKLES} Paso: {SPARKLES} {flow.state} {SPARKLES} {response}{RESET}") # Inicia el flujo
        if flow.state == "fin":
            break
