import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

from src.utils.utils import BLUE, RESET
# from frontend.scss_watcher import watch_scss

os.environ["PYTHONPATH"] = str(Path(".").resolve())

def main():
    # Paths
    main_path = Path("frontend")
      
    # Iniciar Streamlit
    print(f"\n{BLUE}🃏 Iniciando aplicación Streamlit...{RESET}\n")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(main_path / "app.py")],  # Especificar el archivo directamente
        cwd="."  # Asegurar que el directorio raíz sea el contexto
    )
    
    # Abrir el navegador
    webbrowser.open("http://localhost:8501")

    # Configuración de rutas
    SCSS_DIRECTORY = "frontend/static/scss"  # Directorio SCSS
    CSS_DIRECTORY = "frontend/static/css"    # Directorio CSS

    # watch_scss(SCSS_DIRECTORY, CSS_DIRECTORY) 

# def main():
#     tarot_rag = TarotRAG()
#     cards = ["El Sol","La Emperatriz","El Loco","La Estrella","El Mundo","El Mago"]
#     asking = "¿Encontraré el amor este año?"
#     info = "Teletrabajo en informatica y no salgo nunca de casa."
#     tarot_rag.tirada(self,cards, asking, info)

if __name__ == "__main__":
    main()