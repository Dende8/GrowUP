"""
Modulo comun: conexion a la base de datos y columnas derivadas.

Reutiliza exactamente la misma logica ya validada en el notebook
08_validacion_recomendaciones.ipynb, para que las cifras del informe
coincidan siempre con las del analisis exploratorio.
"""

import os
import sys

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src import db_connection as dbc  # noqa: E402

ORDEN_DIAS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NOMBRES_DIAS_ES = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miercoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sabado", "Sunday": "Domingo",
}
UMBRAL_SHORT_SEGUNDOS = 180
MIN_DIAS_PARA_VELOCIDAD = 7
DIAS_EUROPEOS = ["Tuesday", "Wednesday"]
MESES_VENTANA_FICHAJES = {1, 6, 7, 8}
NOMBRES_MESES_VENTANA = "enero, junio, julio y agosto"


def _get_engine():
    url = dbc.DATABASE_URL or (
        f"postgresql+psycopg2://{dbc.DB_CONFIG['user']}:{dbc.DB_CONFIG['password']}"
        f"@{dbc.DB_CONFIG['host']}:{dbc.DB_CONFIG['port']}/{dbc.DB_CONFIG['dbname']}"
    )
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return create_engine(url)


@st.cache_data(ttl=600)
def cargar_datos():
    """
    Carga las tablas necesarias y anade todas las columnas derivadas
    usadas en el informe. Cacheado 10 minutos para no golpear la base
    de datos en cada cambio de seccion.
    """
    engine = _get_engine()

    canal = pd.read_sql("SELECT * FROM canal", engine)
    video = pd.read_sql("SELECT * FROM video", engine, parse_dates=["fecha_publicacion"])
    retencion = pd.read_sql("SELECT * FROM retencion_audiencia", engine)
    evolucion = pd.read_sql("SELECT * FROM evolucion_diaria", engine, parse_dates=["fecha"])

    evolucion["dia_semana"] = evolucion["fecha"].dt.day_name()
    evolucion["suscriptores_netos"] = evolucion["subscribers_gained"] - evolucion["subscribers_lost"]

    hoy = pd.Timestamp.now().normalize()

    video["es_short"] = video["duracion_segundos"] <= UMBRAL_SHORT_SEGUNDOS
    video["formato"] = video["es_short"].map({True: "Short", False: "Largo"})
    video["dia_semana_publicacion"] = video["fecha_publicacion"].dt.day_name()
    video["mes_publicacion"] = video["fecha_publicacion"].dt.month

    video["antiguedad_dias"] = (hoy - video["fecha_publicacion"]).dt.days.clip(lower=1)
    video["views_por_dia"] = video["views_totales"] / video["antiguedad_dias"]
    video["apto_velocidad"] = video["antiguedad_dias"] >= MIN_DIAS_PARA_VELOCIDAD

    video["ratio_likes_vista"] = video["likes"] / video["views_totales"]
    video["ratio_comentarios_vista"] = video["comentarios"] / video["views_totales"]
    video["z_views_categoria_formato"] = video.groupby(["categoria", "formato"])["views_totales"].transform(
        lambda s: (s - s.mean()) / s.std() if s.std() > 0 else 0
    )

    retencion_media_por_video = retencion.groupby("video_id")["audience_watch_ratio"].mean().rename("retencion_media")
    video = video.merge(retencion_media_por_video, on="video_id", how="left")

    patron_semanal_audiencia = evolucion.groupby("dia_semana")["views"].mean().reindex(ORDEN_DIAS)
    dias_fuertes = patron_semanal_audiencia.sort_values(ascending=False).head(2).index.tolist()
    video["es_dia_fuerte"] = video["dia_semana_publicacion"].isin(dias_fuertes)
    video["es_dia_europeo"] = video["dia_semana_publicacion"].isin(DIAS_EUROPEOS)
    video["dia_relevante_partido"] = video["es_dia_fuerte"] | video["es_dia_europeo"]
    video["en_ventana_fichajes"] = video["mes_publicacion"].isin(MESES_VENTANA_FICHAJES)

    return {
        "canal": canal,
        "video": video,
        "evolucion": evolucion,
        "patron_semanal_audiencia": patron_semanal_audiencia,
        "dias_fuertes": dias_fuertes,
    }


def dia_es(nombre_ingles: str) -> str:
    """Traduce un nombre de dia de la semana de ingles a espanol."""
    return NOMBRES_DIAS_ES.get(nombre_ingles, nombre_ingles)
