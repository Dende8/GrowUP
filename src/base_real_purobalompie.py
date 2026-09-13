"""
Fase 4 - Paso 1: cargar y limpiar los datos REALES de @PuroBalompie
(extraídos en la Fase 2 con la Data API v3) y resumirlos en un
conjunto de "patrones" (duración típica, ratio de likes/vista,
frecuencia de publicación...) que usaremos como base estadística
para generar los datos sintéticos de Golazo.

Nada en este módulo inventa datos: solo lee y resume lo que ya
existe en /raw/purobalompie_videos_detail.json.
"""

import json
import os
import re

import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")


def _duracion_iso8601_a_segundos(duracion: str) -> int:
    """Misma función validada en la Fase 2 (notebooks/01)."""
    patron = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
    match = patron.match(duracion)
    horas, minutos, segundos = (int(x) if x else 0 for x in match.groups())
    return horas * 3600 + minutos * 60 + segundos


def cargar_videos_purobalompie() -> pd.DataFrame:
    """
    Carga purobalompie_videos_detail.json, lo aplana y limpia los
    tipos (vistas/likes/comentarios a numérico, duración a segundos,
    fecha de publicación a datetime), tal y como se validó en la
    Fase 2.
    """
    ruta = os.path.join(RAW_DIR, "purobalompie_videos_detail.json")
    with open(ruta, encoding="utf-8") as f:
        videos = json.load(f)

    df = pd.json_normalize(videos)

    df["duracion_segundos"] = df["contentDetails.duration"].apply(
        _duracion_iso8601_a_segundos
    )
    for col in ["statistics.viewCount", "statistics.likeCount", "statistics.commentCount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["fecha_publicacion"] = pd.to_datetime(df["snippet.publishedAt"])

    return df[
        [
            "id",
            "snippet.title",
            "fecha_publicacion",
            "duracion_segundos",
            "statistics.viewCount",
            "statistics.likeCount",
            "statistics.commentCount",
        ]
    ].rename(
        columns={
            "snippet.title": "titulo",
            "statistics.viewCount": "views",
            "statistics.likeCount": "likes",
            "statistics.commentCount": "comentarios",
        }
    )


def cargar_estadisticas_canal_purobalompie() -> dict:
    """
    Carga las estadísticas públicas del canal (suscriptores incluidos),
    extraídas en la Fase 2 con channels.list.
    """
    ruta = os.path.join(RAW_DIR, "purobalompie_channel.json")
    with open(ruta, encoding="utf-8") as f:
        canal = json.load(f)
    return {
        "suscriptores": int(canal["statistics"]["subscriberCount"]),
    }


def resumen_patrones(df: pd.DataFrame) -> dict:
    """
    Reduce el DataFrame real de PuroBalompie a un puñado de patrones
    reutilizables: no copiamos sus cifras absolutas de vistas tal
    cual (su canal es de otra escala), pero SÍ guardamos su
    distribución completa de vistas (para hacer bootstrap) junto con
    sus suscriptores reales, de forma que se pueda reescalar por
    RATIO DE SUSCRIPTORES en vez de por el vídeo más viral del canal
    (que sería muy sensible a un único outlier).
    """
    df = df.sort_values("fecha_publicacion")
    intervalos_dias = df["fecha_publicacion"].diff().dt.days.dropna()
    stats_canal = cargar_estadisticas_canal_purobalompie()

    # Winsorización: capamos las vistas al percentil 90 antes de
    # guardarlas para el bootstrap. Sin esto, un único vídeo viral
    # puntual de la muestra real puede "clonarse" varias veces al
    # remuestrear con reemplazo (más probable cuanto más pequeña es
    # la muestra real), generando decenas de falsos vídeos virales
    # sintéticos que no reflejan un patrón real del canal.
    limite_p90 = df["views"].quantile(0.90)
    views_capadas = df["views"].clip(upper=limite_p90)

    return {
        "duracion_media_seg": float(df["duracion_segundos"].mean()),
        "duracion_std_seg": float(df["duracion_segundos"].std()),
        "duraciones_absolutas": df["duracion_segundos"].tolist(),
        "ratio_likes_por_vista": float((df["likes"] / df["views"]).median()),
        "ratio_comentarios_por_vista": float((df["comentarios"] / df["views"]).median()),
        "intervalo_publicacion_dias_mediana": float(intervalos_dias.median()),
        "suscriptores": stats_canal["suscriptores"],
        # Vistas ABSOLUTAS reales (capadas al p90) para hacer
        # bootstrap conservando la forma de la distribución sin dejar
        # que un único outlier domine el remuestreo.
        "views_absolutas": views_capadas.tolist(),
    }


if __name__ == "__main__":
    df = cargar_videos_purobalompie()
    patrones = resumen_patrones(df)
    print(f"Vídeos reales cargados de PuroBalompie: {len(df)}")
    for k, v in patrones.items():
        if k == "views_absolutas":
            continue
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
