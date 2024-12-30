import sys  # Para manejar entradas y salidas del sistema
from llm_agent import LLMAgent  # Para interactuar con el modelo de lenguaje
from flow_manager import FlowManager  # Para manejar el flujo de interacciones
from utils.utils import get_env_key, THINKING, BRIGHT_GREEN, TURQUOISE, PASTEL_YELLOW, SPARKLES, RESET, RED, RAISED_HAND
import re  # Para validación de patrones

class ValidatorAgent:
    def __init__(self, llm_agent, flow_manager, base_prompt):
        """
        Inicializa la clase ValidatorAgent con un estado inicial,
        un agente LLM y un administrador de flujo.
        """
        self.state = "INTRODUCTION"  # Estado inicial de la interacción
        self.llm_agent = llm_agent  # Instancia del agente LLM
        self.flow_manager = flow_manager  # Instancia de FlowManager
        self.messages = [{"role": "system", "content": base_prompt}]  # Mensajes iniciales
    def is_disrespectful(self, user_response):
        """
        Verifica si la respuesta del usuario contiene una falta de respeto.
        """
        # Prepara el mensaje para el modelo de lenguaje
        disrespect_prompt = (
            "Recuerda tu eres LAILA. Tu tarea ahora es verificar si este texto te está faltando al respeto:\n"
            f"Texto: '{user_response}'\n\n"
            "¿El texto te falta al respeto?"
            "Responde únicamente 'Sí' o 'No'."
        )

        try:
            # Llama al agente LLM para analizar el texto
            offended_response = self.llm_agent.generate_response('assistant', disrespect_prompt)
            print(f"\n{PASTEL_YELLOW}{THINKING} Contiene una falta de respeto?{RESET} {'Sí' in offended_response}")  # Imprime la respuesta completa del LLM para depuración
            # Devuelve True si el modelo identifica una falta de respeto
            return "Sí" in offended_response
        except Exception as e:
            print(f"{RED}Error al verificar falta de respeto: {e}{RESET}")
            return False
        
    def generate_laila_response(self, tone):
        """
        Genera una respuesta dinámica utilizando el LLM en función del contexto proporcionado.
        """
        try:
            return self.llm_agent.generate_response("assistant", f"Por favor, responde muy dramática y {tone}")
        except Exception as e:
            print(f"{RED}Error al generar respuesta con LLM: {e}{RESET}")
            return "Lo siento, hubo un error al generar mi respuesta."
        
    def handle_interaction(self, user_input):
        """
        Maneja la interacción con el usuario según el estado actual.
        """
        if self.flow_manager.can_continue():
            if self.state == "INTRODUCTION":
                if self.is_disrespectful(user_input):
                    print('Es ofensivo')
                    return self.generate_laila_response("ofendida")
                else: 
                    # 
                    self.state = "QUESTION_1"  
                    self.flow_manager.advance()
                    self.messages.append({"role": "user", "content": user_input.strip()})
                    self.messages.append({"role": "assistant", "content": f"Por favor, responde muy dramática y curiosa"})
                    return self.llm_agent.generate_response('assistant', get_env_key('PROMPT_QUESTION_1')) 
            
            if self.state == "QUESTION_1":
                if self.is_disrespectful(user_input):
                    print('Es ofensivo')
                    return self.generate_laila_response("ofendida")
                else: 
                    # 
                    self.state = "QUESTION_2"  
                    self.flow_manager.advance()
                    return self.llm_agent.generate_response('assistant', get_env_key('PROMPT_QUESTION_2')) 

            if self.state == "QUESTION_2":
                if self.is_disrespectful(user_input):
                    print('Es ofensivo')
                    return self.generate_laila_response("ofendida")
                else: 
                    # 
                    self.state = "QUESTION_3"  
                    self.flow_manager.advance()
                    return self.llm_agent.generate_response('assistant', get_env_key('PROMPT_QUESTION_3'))
                
            if self.state == "QUESTION_3":
                if self.is_disrespectful(user_input):
                    print('Es ofensivo')
                    return self.generate_laila_response("ofendida")
                else: 
                    # 
                    self.state = "QUESTION_4"  
                    self.flow_manager.advance()
                    return self.llm_agent.generate_response('assistant', get_env_key('PROMPT_QUESTION_4'))

            if self.state == "QUESTION_4":
                if self.is_disrespectful(user_input):
                    print('Es ofensivo')
                    return self.generate_laila_response("ofendida")
                else: 
                    # 
                    self.state = "FINISH"  
                    self.flow_manager.advance()
                    return self.llm_agent.generate_response('assistant', get_env_key('FINISH'))                

        else:
            print(f"{PASTEL_YELLOW}{RAISED_HAND} Finaliza el flujo{RESET}")
            # Finalizar interacción
            response = "Lo siento... el misterio me reclama... Espero haberte ayudado. Hasta pronto, cariño."
            self.flow_manager.finish()
            return response

def main():
    try:
        prompt_file = get_env_key("PROMPT_FILE")
        with open(prompt_file, "r", encoding="utf-8") as file:
            base_prompt = file.read()
    except FileNotFoundError:
        print(f"{RED}Error: No se encontró el archivo de prompt.{RESET}")
        return

    llm_agent = LLMAgent([], llm_model="llama-3.3-70b-versatile")
    flow_manager = FlowManager(max_steps=10)
    validator_agent = ValidatorAgent(llm_agent, flow_manager, base_prompt)

    while True:
        try:
            user_input = input(f"{TURQUOISE}✨ Dime algo, cariño: {RESET}")
            if user_input.lower() in {"salir", "exit"}:
                print(f"{RED}✨ ¡Adiós, cariño! El universo te acompaña siempre.{RESET}")
                break

            response = validator_agent.handle_interaction(user_input)
            print(response)
        except Exception as e:
            print(f"{RED}Error en la interacción: {e}{RESET}")

if __name__ == "__main__":
    main()
