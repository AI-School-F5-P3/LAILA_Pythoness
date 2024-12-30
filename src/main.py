import os
import streamlit as st
from chat_app import ChatApp
from utils.utils import local_css


def main():
    # Cargar configuración y CSS
    local_css(os.path.join(os.path.dirname(__file__), '../frontend/static', 'style.css'))
    st.header("💬 Chat con LAILA")
    app = ChatApp()
    app.run()

if __name__ == "__main__":
    main()