"""
Configuración del proyecto.

Carga la API key de YouTube desde un archivo .env para no dejarla
nunca escrita directamente en el código (buena práctica de seguridad).
"""

import os
from dotenv import load_dotenv

# Busca un archivo ".env" en la raíz del proyecto y carga sus variables
load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    raise EnvironmentError(
        "No se ha encontrado YOUTUBE_API_KEY. "
        "Copia .env.example como .env y añade tu API key real."
    )

# Nombre del canal que vamos a usar como fuente de datos reales
TARGET_HANDLE = "@PuroBalompie"

# Rutas de salida para los datos crudos
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")
