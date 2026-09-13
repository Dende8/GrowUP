"""
Fase 6 (complemento) - Conexión a la base de datos PostgreSQL.

Soporta dos formas de configurar la conexión, para que el mismo
código sirva tanto en local como en Neon (u otro proveedor):

1. DATABASE_URL: una única cadena de conexión (formato que entrega
   Neon directamente en su panel "Connect"). Si está presente en el
   .env, tiene prioridad.
2. DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD: variables
   sueltas, más cómodas para un Postgres local instalado a mano.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "dbname": os.getenv("DB_NAME", "golazo_growup"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    """
    Abre y devuelve una conexión a la base de datos.
    Usa DATABASE_URL si existe (Neon); si no, las variables sueltas
    (Postgres local).
    """
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL)
    return psycopg2.connect(**DB_CONFIG)


def test_connection():
    """Prueba la conexión y muestra las tablas existentes."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"Conexión correcta a: {version}")

            cur.execute("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tablas = [fila[0] for fila in cur.fetchall()]
            print(f"Tablas encontradas ({len(tablas)}): {', '.join(tablas)}")


if __name__ == "__main__":
    test_connection()
