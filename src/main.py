from flow_manager import FlowManager
from llm_agent import LLMAgent
from validator_agent import ValidatorAgent
from utils.utils import get_env_key, TURQUOISE, SPARKLES, RESET,RED

def main():
    # Cargar el prompt inicial de LAILA
    prompt_file = get_env_key("PROMPT_FILE")
    with open(prompt_file, "r", encoding="utf-8") as file:
        base_prompt = file.read()

    # Inicialización
    flow_manager = FlowManager(max_interactions=3)  # Control de interacciones
    llm_agent = LLMAgent()
    validator_agent = ValidatorAgent()
    messages = [{"role": "system", "content": base_prompt}]

    while flow_manager.can_continue():
        # Solicitar una pregunta del LLM
        llm_response = llm_agent.generate_response(messages)
        print(f"{TURQUOISE}{SPARKLES}  {llm_response}{RESET}")

        while True:
            # Entrada del usuario
            user_input = input("Tú: ").strip()

            # 1. Verificar falta de respeto
            if validator_agent.is_disrespectful(user_input):
                messages.append({"role": "user", "content": user_input})
                messages.append({"role": "assistant", "content": "Responde ofendida"})
                offended_response = llm_agent.generate_response(messages)
                print(f"{TURQUOISE}{SPARKLES}  {offended_response}{RESET}")
                #TODO cambiar de pantalla en frontend.

                return  # Salir inmediatamente de la app

            # 2. Validar respuesta (flujo normal)
            is_valid = validator_agent.validate(flow_manager.current_interaction + 1, user_input)
            is_valid_tarot_question = validator_agent.is_valid_tarot_question(user_input)

            if is_valid:
                # Respuesta válida
                if not is_valid_tarot_question:
                    # Pregunta no válida
                    messages.append({"role": "user", "content": f"La pregunta no es válida para el tarot: '{user_input}'"})
                    messages.append({"role": "user", "content": "Eres LAILA, debes insistir en una pregunta válida y ofrecer ejemplos."})
                    not_tarot_response = llm_agent.generate_response(messages)
                    print(f"{TURQUOISE}{SPARKLES}  {not_tarot_response}{RESET}")
                    break
                else:
                    print("vale")
            else:
                # Respuesta poco clara
                messages.append({"role": "user", "content": f"La respuesta no ha sido clara: '{user_input}'"})
                messages.append({"role": "user", "content": "Responde como LAILA insistiendo en que el usuario sea claro."})
                unclear_response = llm_agent.generate_response(messages)
                print(f"{TURQUOISE}{SPARKLES}  {unclear_response}{RESET}")


        flow_manager.increment()

    # Generar la respuesta final dinámica de LAILA
    messages.append({"role": "user", "content": "Finaliza la tirada con un mensaje místico, solemne y teatral, como LAILA suele hacer."})
    final_response = llm_agent.generate_response(messages)
    print(f"\n{TURQUOISE}{SPARKLES}  {final_response}{RESET}\n")

if __name__ == "__main__":
    main()
