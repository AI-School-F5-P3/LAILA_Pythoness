import os
import streamlit as st
from src.chat_app import ChatApp
from src.utils.utils import local_css
from PIL import Image

def main():
    # Cargar configuración y CSS
    local_css(os.path.join(os.path.dirname(__file__), 'static/css', 'styles.css'))
    with st.container(key="header"):
        # Mostrar spinner mientras se carga la imagen
        with st.spinner(''):
            try:
                import time
                time.sleep(0)
                # Simula la carga de la imagen (puedes optimizar según tu caso)
                image_path = "frontend/static/img/laila_header.png"
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    st.image(image)
                else:
                    st.error("No se encontró la imagen.")
            except Exception as e:
                st.error(f"Error al cargar la imagen: {e}")

    # Inicializar la aplicación
    app = ChatApp()
    app.run()

if __name__ == "__main__":
    main()
