from langchain_groq import ChatGroq
from openai import OpenAI
from utils.utils import get_env_key, THINKING, TURQUOISE, PASTEL_YELLOW, SPARKLES, RESET, RED

class LLMAgent:

    def __init__(self, messages, llm_model="llama-3.3-70b-versatile"):
        """
        Inicializa el agente LLM usando Groq API y el modelo especificado.
        """
        self.llm_model = llm_model
        self.messages = messages

    def validate_message_format(self, message):
        """
        Valida que el mensaje tenga el formato correcto.
        """
        if not isinstance(message, dict):
            raise ValueError("Cada mensaje debe ser un diccionario.")
        if "role" not in message or "content" not in message:
            raise ValueError("Cada mensaje debe contener las claves 'role' y 'content'.")
        if not isinstance(message["role"], str) or not isinstance(message["content"], str):
            raise ValueError("Los valores de 'role' y 'content' deben ser cadenas.")

    def add_message(self, role, content):
        """
        Agrega un mensaje validado al historial.
        """
        new_message = {"role": role, "content": content}
        # self.validate_message_format(new_message)
        self.messages.append(new_message)
        # print(self.messages)

    def debug_messages(self):
        """
        Depura el contenido del historial de mensajes.
        """
        # for idx, message in enumerate(self.messages):
        #     print(f"Mensaje {idx}: {message}")

    def generate_response_openai(self, role, prompt):
        """
        Genera una respuesta utilizando OpenAI API.
        """
        self.openai_api_key = get_env_key('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        try:
            self.add_message(role, prompt)
            self.debug_messages()

            # Realizar la llamada a la API de OpenAI
            completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=self.messages,
                temperature=0.2,
                max_tokens=250,
            )
            response_content = completion.choices[0].message.content
            self.add_message("assistant", response_content)
            return response_content
        except Exception as e:
            return f"Error al obtener la respuesta de OpenAI: {str(e)}"

    def generate_response_groq(self, role, prompt):
        """
        Genera una respuesta utilizando Groq API.
        """
        groq_api_key = get_env_key('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("La clave GROQ_API_KEY no está definida en las variables de entorno.")
        else:
            client = ChatGroq(
                groq_api_key=groq_api_key,
                model_name=self.llm_model,
                max_tokens=500,
                max_retries=4,
                verbose=False
            )
            try:
                self.add_message(role, prompt)
                # self.debug_messages()

                response = client.invoke(prompt)
                response_content = response.content
                # self.add_message("assistant", response_content)
                return response_content
            except Exception as e:
                print(prompt)
                return f"Error en Groq: {str(e)}"

    def generate_response(self, role, prompt):
        """
        Genera una respuesta utilizando el modelo especificado.
        """
        # print(self.messages)
        if self.llm_model.startswith("gpt-"):
            return self.generate_response_openai(role,prompt)
        else:
            return self.generate_response_groq(role,prompt)