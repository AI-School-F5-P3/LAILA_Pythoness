from groq import Groq
from openai import OpenAI
from src.faiss_index import FaissIndex
from src.utils.utils import get_env_key


class LlmClient:
    """Clase para manejar la interacción con Groq."""
    # model = "gpt-3.5-turbo-0125"
    model = "llama-3.3-70b-versatile"
    # model = "gemma2-9b-it"
    # model = "mixtral-8x7b-32768" # No responde bien... 
    # model = "llama-3.1-8b-instant"
    # model = "llama3-8b-8192"
    def __init__(self, llm_model=model):
        self.llm_model = llm_model
        self.index = FaissIndex()
        self.index.load_index()
        

        if self.llm_model.startswith("gpt-"):
            openai_api_key = get_env_key('OPENAI_API_KEY')
            if not openai_api_key:
                raise ValueError("La clave OPENAI_API_KEY no está definida en las variables de entorno.")
            self.client = OpenAI(api_key=openai_api_key)
        else:           
            groq_api_key = get_env_key('GROQ_API_KEY')
            if not groq_api_key:
                raise ValueError("La clave GROQ_API_KEY no está definida en las variables de entorno.")
            self.client = Groq()
        

    def get_response(self, messages_with_context):
        user_query = messages_with_context[-1]['content']
        relevant_docs = self.index.search(user_query, top_k=3, max_characters=2000)
        context = "\n".join(relevant_docs)
        
        # Verifica que el contexto no exceda el límite del modelo
        if len(context) > 500000:
            raise ValueError("El contexto generado es demasiado grande. Ajusta el tamaño del índice o reduce los documentos.")
        
        messages_with_context.append({
            "role": "system",
            "content": f"Usa solo esta información para responder:\n{context}"
        })
        response_stream = self.client.chat.completions.create(
            messages=messages_with_context,
            model=self.llm_model,
            temperature=0.2,
            max_tokens=1024,
            top_p=1,
            stream=True
        )

        response_text = ""
        for chunk in response_stream:
            try:
                # Extraer contenido del primer choice y delta
                content = chunk.choices[0].delta.content
                if content:  # Ignorar si es None
                    response_text += content
            except (AttributeError, IndexError, KeyError) as e:
                print(f"Error al procesar chunk: {e}")

        if not response_text:
            raise ValueError("El flujo de respuesta está vacío o no contiene texto válido.")

        return response_text