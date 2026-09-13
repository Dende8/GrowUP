"""
Fase 7 - Carga de datos en la base de datos.

Vuelca en las tablas creadas en la Fase 6:
 - el catálogo sintético de vídeos de Golazo (+ tags derivados de su categoría)
 - los 5 informes de Analytics sintéticos: evolucion_diaria,
   retencion_audiencia, demografia, trafico, ingresos

Es IDEMPOTENTE: puede ejecutarse varias veces sin duplicar ni
acumular datos. Al empezar hace TRUNCATE ... CASCADE desde `canal`,
lo que borra automáticamente todo lo que cuelga de él (video,
video_tag, retencion_audiencia, evolucion_diaria, demografia,
trafico, ingresos) y vuelve a cargarlo todo desde cero.

Requisito previo:
    python -m src.generador_sintetico
(genera /synthetic/golazo_catalogo_videos.csv y
 /synthetic/golazo_analytics_sintetico.json)

Ejecución:
    python -m src.cargar_datos
"""

import json
import os
from datetime import date

import pandas as pd
from psycopg2.extras import execute_values

from . import db_connection as dbc

SYNTHETIC_DIR = os.path.join(os.path.dirname(__file__), "..", "synthetic")

CHANNEL_ID = "golazo"

# Datos reales conocidos del cliente (los únicos no sintéticos de esta carga)
CANAL_INFO = {
    "channel_id": CHANNEL_ID,
    "titulo": "Golazo",
    "descripcion": "Canal de seguimiento de un equipo de fútbol: opinión post-partido, fichajes y afición.",
    "custom_url": "@golazo",
    "pais": "ES",
    "fecha_creacion": date(2015, 4, 11),
    "suscriptores": 14_000,
    "total_videos": 338,
}

# Tags sintéticos derivados de la categoría de contenido (no venían
# generados en la Fase 4; se derivan aquí de forma determinista).
TAGS_POR_CATEGORIA = {
    "Seguimiento del club": ["futbol", "liga", "club"],
    "Opinión post-partido": ["opinion", "analisis", "partido"],
    "Fichajes": ["fichajes", "mercado", "rumores"],
    "Afición": ["aficion", "hinchada", "estadio"],
    "Curiosidades de fútbol": ["curiosidades", "futbol", "datos"],
}


def truncar_todo(conn):
    """Borra todos los datos existentes (en cascada desde canal) para
    que el script se pueda relanzar sin duplicar filas."""
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE canal CASCADE;")


def cargar_canal(conn, vistas_totales: int):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO canal
                (channel_id, titulo, descripcion, custom_url, pais,
                 fecha_creacion, suscriptores, total_videos, vistas_totales)
            VALUES (%(channel_id)s, %(titulo)s, %(descripcion)s, %(custom_url)s,
                    %(pais)s, %(fecha_creacion)s, %(suscriptores)s,
                    %(total_videos)s, %(vistas_totales)s)
            """,
            {**CANAL_INFO, "vistas_totales": vistas_totales},
        )


def cargar_videos_y_tags(conn, df_catalogo: pd.DataFrame):
    videos = [
        (
            fila.video_id, CHANNEL_ID, fila.titulo, fila.categoria,
            fila.fecha_publicacion, int(fila.duracion_segundos),
            int(fila.views_totales), int(fila.likes), int(fila.comentarios),
        )
        for fila in df_catalogo.itertuples()
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO video
                (video_id, channel_id, titulo, categoria, fecha_publicacion,
                 duracion_segundos, views_totales, likes, comentarios)
            VALUES %s
            """,
            videos,
        )

        tags = [
            (fila.video_id, tag)
            for fila in df_catalogo.itertuples()
            for tag in TAGS_POR_CATEGORIA.get(fila.categoria, [])
        ]
        execute_values(
            cur, "INSERT INTO video_tag (video_id, tag) VALUES %s", tags
        )

    return len(videos), len(tags)


def cargar_evolucion_diaria(conn, informe: dict) -> int:
    with conn.cursor() as cur:
        filas = [(CHANNEL_ID, *fila) for fila in informe["rows"]]
        execute_values(
            cur,
            """
            INSERT INTO evolucion_diaria
                (channel_id, fecha, views, estimated_minutes_watched,
                 average_view_duration, subscribers_gained, subscribers_lost)
            VALUES %s
            """,
            filas,
        )
    return len(filas)


def cargar_retencion(conn, informe: dict) -> int:
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO retencion_audiencia
                (video_id, elapsed_video_time_ratio, audience_watch_ratio,
                 relative_retention_performance)
            VALUES %s
            """,
            informe["rows"],
        )
    return len(informe["rows"])


def cargar_demografia(conn, informe: dict) -> int:
    with conn.cursor() as cur:
        filas = [(CHANNEL_ID, *fila) for fila in informe["rows"]]
        execute_values(
            cur,
            "INSERT INTO demografia (channel_id, age_group, gender, viewer_percentage) VALUES %s",
            filas,
        )
    return len(filas)


def cargar_trafico(conn, informe: dict) -> int:
    with conn.cursor() as cur:
        filas = [(CHANNEL_ID, *fila) for fila in informe["rows"]]
        execute_values(
            cur,
            "INSERT INTO trafico (channel_id, traffic_source_type, views, estimated_minutes_watched) VALUES %s",
            filas,
        )
    return len(filas)


def cargar_ingresos(conn, informe: dict) -> int:
    with conn.cursor() as cur:
        filas = [(CHANNEL_ID, *fila) for fila in informe["rows"]]
        execute_values(
            cur,
            """
            INSERT INTO ingresos
                (channel_id, fecha, estimated_revenue, estimated_ad_revenue,
                 cpm, playback_based_cpm)
            VALUES %s
            """,
            filas,
        )
    return len(filas)


def verificar_carga(conn):
    tablas = [
        "canal", "video", "video_tag", "evolucion_diaria",
        "retencion_audiencia", "demografia", "trafico", "ingresos",
    ]
    with conn.cursor() as cur:
        print("\nRecuento final por tabla:")
        for tabla in tablas:
            cur.execute(f"SELECT COUNT(*) FROM {tabla};")
            print(f"  {tabla:22s}: {cur.fetchone()[0]}")


def main():
    df_catalogo = pd.read_csv(os.path.join(SYNTHETIC_DIR, "golazo_catalogo_videos.csv"))
    with open(os.path.join(SYNTHETIC_DIR, "golazo_analytics_sintetico.json"), encoding="utf-8") as f:
        analytics = json.load(f)

    conn = dbc.get_connection()
    try:
        print("Vaciando tablas existentes (TRUNCATE ... CASCADE desde canal)...")
        truncar_todo(conn)

        print("Cargando canal...")
        cargar_canal(conn, vistas_totales=int(df_catalogo["views_totales"].sum()))

        print("Cargando catálogo de vídeos y tags...")
        n_videos, n_tags = cargar_videos_y_tags(conn, df_catalogo)
        print(f"  -> {n_videos} vídeos, {n_tags} tags")

        print("Cargando evolución diaria...")
        print(f"  -> {cargar_evolucion_diaria(conn, analytics['evolucion_diaria'])} filas")

        print("Cargando retención de audiencia...")
        print(f"  -> {cargar_retencion(conn, analytics['retencion_audiencia'])} filas")

        print("Cargando demografía...")
        print(f"  -> {cargar_demografia(conn, analytics['demografia'])} filas")

        print("Cargando tráfico...")
        print(f"  -> {cargar_trafico(conn, analytics['trafico'])} filas")

        print("Cargando ingresos...")
        print(f"  -> {cargar_ingresos(conn, analytics['ingresos'])} filas")

        conn.commit()
        print("\nCarga completada y confirmada (commit).")
        verificar_carga(conn)

    except Exception:
        conn.rollback()
        print("\nERROR durante la carga: se ha revertido todo (rollback). No queda nada a medias.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
