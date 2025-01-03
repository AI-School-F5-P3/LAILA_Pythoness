from src.rag import RAG
from src.llm_client import LlmClient

class TarotRAG:
    def __init__(self):
        self.rag = RAG()  # Carga el índice una vez al crear la instancia
        self.llm_client = LlmClient()

    def rag_question(self, question):
        response = self.rag.ask_question(question)
        return response  # Retorna la respuesta correctamente
    def tirada(self,cards,asking,info):
        # Utilizando un bucle para recopilar la información de todas las cartas
        cards_info = [self.rag_question(f"Dame toda la información sobre la carta {card}") for card in cards]
        # Agregando la explicación de la tirada al final
        cards_info.append(self.rag_question("Explícame la tirada 'Pirámide Invertida de 6 cartas'"))
        info_cards = "\n".join(cards_info)
        # print("Información Recopilada:\n", info_cards)

        # Interacción con el modelo LLM
        conversation_history = []
        question = f"Se ha hecho una tirada (Piramide invertida de 6 cartas) y han salido en este orden: {cards}. Pregunta: {asking}. Info adicional: {info}."
        print(question)
        conversation_history.append({"role": "system", "content": f"## CONTEXTO:\n{info_cards}"})
        conversation_history.append({"role": "user", "content": question})
        response = self.llm_client.get_response(conversation_history)
        print(f"RAG: {response}")
        return response

