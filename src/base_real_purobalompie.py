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


def resumen_patrones(df: pd.DataFrame) -> dict:
    """
    Reduce el DataFrame real de PuroBalompie a un puñado de patrones
    reutilizables: no copiamos sus cifras absolutas (su canal es de
    otra escala), sino RATIOS y FORMAS de distribución que sí son
    transferibles a un canal de fútbol más pequeño como Golazo.
    """
    df = df.sort_values("fecha_publicacion")
    intervalos_dias = df["fecha_publicacion"].diff().dt.days.dropna()

    return {
        "duracion_media_seg": float(df["duracion_segundos"].mean()),
        "duracion_std_seg": float(df["duracion_segundos"].std()),
        "ratio_likes_por_vista": float((df["likes"] / df["views"]).median()),
        "ratio_comentarios_por_vista": float((df["comentarios"] / df["views"]).median()),
        "intervalo_publicacion_dias_mediana": float(intervalos_dias.median()),
        # Forma relativa de la distribución de vistas (normalizada 0-1
        # sobre la vista máxima del canal), para poder "re-escalarla"
        # al tamaño de audiencia de Golazo sin copiar cifras absolutas.
        "views_normalizadas": (df["views"] / df["views"].max()).tolist(),
    }


if __name__ == "__main__":
    df = cargar_videos_purobalompie()
    patrones = resumen_patrones(df)
    print(f"Vídeos reales cargados de PuroBalompie: {len(df)}")
    for k, v in patrones.items():
        if k != "views_normalizadas":
            print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
