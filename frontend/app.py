import os
import streamlit as st
from src.chat_app import ChatApp
from src.utils.utils import local_css


def main():
    # Cargar configuración y CSS
    local_css(os.path.join(os.path.dirname(__file__), 'static/css', 'styles.css'))
    with st.container(key="header"):
        st.image("frontend/static/img/laila_header.png")    
    app = ChatApp()
    app.run()

if __name__ == "__main__":
    main()