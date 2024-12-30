import streamlit as st

class ChatHistory:
    """Clase para manejar el histórico de mensajes."""
    def __init__(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def add_message(self, role, content, hidden=False):
        """Añade un mensaje al historial."""
        st.session_state.messages.append({"role": role, "content": content, "hidden": hidden})

    def get_messages(self):
        """Obtiene todos los mensajes, eliminando la propiedad `hidden`."""
        return [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]

    def get_visible_messages(self):
        """Obtiene solo los mensajes que no están ocultos."""
        return [msg for msg in st.session_state.messages if not msg.get("hidden", False)]

    def display_message(self, message):
        """Muestra un único mensaje."""
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def display_messages(self):
        """Muestra solo los mensajes visibles del historial."""
        for message in self.get_visible_messages():
            self.display_message(message)