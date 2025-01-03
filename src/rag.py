from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from src.llm_client import LlmClient
import os
import pickle
import torch

class RAG:
    def __init__(self, data_dir="data", index_file="faiss_index.pkl"):
        self.index_file = index_file
        self.docs = []

        # Intentar cargar índice FAISS desde archivo
        if os.path.exists(self.index_file):
            print("Cargando índice FAISS desde archivo...")
            with open(self.index_file, 'rb') as f:
                self.db = pickle.load(f)
                self.retriever = self.db.as_retriever(search_kwargs={"k": 4})
        else:
            print("El archivo de índice no existe. Creando un nuevo índice FAISS...")
            self._create_index(data_dir)

        # Inicializar LLM Client
        self.llm_client = LlmClient()

    def _create_index(self, data_dir):
        # Cargar documentos desde la carpeta 'data'
        for file_name in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file_name)
            if file_name.endswith(".txt"):
                loader = TextLoader(file_path)
            elif file_name.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:
                print(f"Formato no soportado: {file_name}")
                continue

            self.docs.extend(loader.load())

        print(f"Documentos cargados: {len(self.docs)}")

        # Dividir los textos
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        self.docs = self.text_splitter.split_documents(self.docs)

        # Configurar Embeddings
        model_path = "sentence-transformers/all-mpnet-base-v2"
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs={'device': 'cuda' if torch.cuda.is_available() else 'cpu'},
            encode_kwargs={'normalize_embeddings': False},
        )

        # Crear FAISS con todos los documentos
        self.db = FAISS.from_documents(self.docs, self.embeddings)
        self.retriever = self.db.as_retriever(search_kwargs={"k": 4})
        print(f"FAISS creado con {len(self.docs)} documentos.")

        # Guardar índice FAISS en archivo
        with open(self.index_file, 'wb') as f:
            pickle.dump(self.db, f)
        print(f"Índice FAISS guardado en {self.index_file}")

    def chat(self):
        """Modo chat interactivo con contexto persistente."""
        print("Bienvenido al chat RAG. Escribe 'salir' para terminar la conversación.")
        conversation_history = []

        while True:
            question = input("Tú: ")
            if question.lower() in ["salir", "exit", "quit"]:
                print("Finalizando la sesión...")
                break

            # Recuperar contexto y generar respuesta
            results = self.retriever.invoke(question)
            context = "\n".join([doc.page_content for doc in results])

            # Agregar la pregunta al historial de conversación
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "system", "content": f"Contexto proporcionado:\n{context}"})

            # Generación de respuesta
            response = self.llm_client.get_response(conversation_history)
            print(f"RAG: {response}")

    def ask_question(self, question):
        """Método para realizar una consulta sin modo chat."""
        results = self.retriever.invoke(question)
        context = "\n".join([doc.page_content for doc in results])
        messages_with_context = [{"role": "user", "content": f"{question}\n\nContexto proporcionado:\n{context}"}]
        response = self.llm_client.get_response(messages_with_context)
        return response

if __name__ == "__main__":
    rag_chat = RAG()
    # response = rag_chat.ask_question("¿En que consiste la piramide invertida de 6 cartas? Responde solo en base al contexto que se te proporcione. No inventes información ni supongas lo que no está dicho. Si algo escapa a tu alcance, simplemente decláralo con la sinceridad de los arcanos. Recuerda, las verdades se revelan, no se fabrican. Si no tienes informacion, responde unicamente '.'") 
    response = rag_chat.ask_question("¿En que consiste la piramide invertida de 6 cartas?")
    print("Respuesta:", response)

