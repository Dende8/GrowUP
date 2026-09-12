"""
Fase 3 - Contrato de datos con la YouTube Analytics API.

Este módulo NO llama a ningún servidor real: define con precisión
- qué parámetros enviaríamos a reports.query en un escenario real
- qué FORMA exacta tendría la respuesta (columnHeaders + rows)

siguiendo el formato documentado oficialmente por Google
(kind: "youtubeAnalytics#resultTable", columnHeaders con
columnType/dataType, rows como listas de valores en el mismo orden
que columnHeaders).

Este "contrato" es el que usaremos en la Fase 4 para generar datos
sintéticos con exactamente la misma estructura que produciría la
API real, y así poder unificarlos sin fricción con los datos reales
de la Data API v3.
"""

import json
import os
from datetime import date

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")

CANAL_ID_SIMULADO = "GOLAZO_CHANNEL_ID_SIMULADO"


def construir_peticion(
    canal_id: str,
    metrics: str,
    dimensions: str | None = None,
    filters: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    """
    Construye el diccionario de parámetros que se enviaría a
    reports.query en un escenario real, es decir:
    youtubeAnalytics.reports().query(**params).execute()
    """
    params = {
        "ids": f"channel=={canal_id}",
        "startDate": start_date.isoformat() if start_date else "2026-08-01",
        "endDate": end_date.isoformat() if end_date else "2026-08-31",
        "metrics": metrics,
    }
    if dimensions:
        params["dimensions"] = dimensions
    if filters:
        params["filters"] = filters
    return params


def forma_respuesta_resulttable(dimensiones: list[str], metricas: list[str]) -> dict:
    """
    Construye la ESTRUCTURA que devolvería la API (sin filas de datos
    todavía) para una combinación de dimensiones + métricas dada,
    replicando el formato real documentado por Google.
    """
    column_headers = []

    for d in dimensiones:
        column_headers.append(
            {"name": d, "columnType": "DIMENSION", "dataType": "STRING"}
        )

    metricas_flotantes = {
        "averageViewDuration", "audienceWatchRatio",
        "relativeRetentionPerformance", "viewerPercentage",
        "estimatedRevenue", "estimatedAdRevenue", "estimatedRedPartnerRevenue",
        "grossRevenue", "cpm", "playbackBasedCpm",
    }
    for m in metricas:
        tipo = "FLOAT" if m in metricas_flotantes else "INTEGER"
        column_headers.append(
            {"name": m, "columnType": "METRIC", "dataType": tipo}
        )

    return {
        "kind": "youtubeAnalytics#resultTable",
        "columnHeaders": column_headers,
        "rows": [],  # Se rellenará con datos sintéticos en la Fase 4
    }


# ---------------------------------------------------------------------
# Informes necesarios para el análisis de Golazo
# ---------------------------------------------------------------------

INFORMES = {
    "evolucion_diaria": {
        "descripcion": "Vistas, tiempo de reproducción y suscriptores día a día",
        "dimensiones": ["day"],
        "metricas": [
            "views",
            "estimatedMinutesWatched",
            "averageViewDuration",
            "subscribersGained",
            "subscribersLost",
        ],
    },
    "retencion_audiencia": {
        "descripcion": "Curva de retención de audiencia por vídeo",
        "dimensiones": ["elapsedVideoTimeRatio"],
        "metricas": ["audienceWatchRatio", "relativeRetentionPerformance"],
    },
    "demografia": {
        "descripcion": "Reparto de la audiencia por edad y género",
        "dimensiones": ["ageGroup", "gender"],
        "metricas": ["viewerPercentage"],
    },
    "trafico": {
        "descripcion": "Fuentes de tráfico que generan vistas",
        "dimensiones": ["insightTrafficSourceType"],
        "metricas": ["views", "estimatedMinutesWatched"],
    },
    "ingresos": {
        "descripcion": "Ingresos estimados día a día",
        "dimensiones": ["day"],
        "metricas": ["estimatedRevenue", "estimatedAdRevenue", "cpm", "playbackBasedCpm"],
    },
}


def generar_contratos() -> dict:
    """
    Genera, para cada informe definido arriba, tanto la petición que
    se enviaría a la API real como la forma exacta de su respuesta.
    """
    contratos = {}
    for nombre, info in INFORMES.items():
        contratos[nombre] = {
            "descripcion": info["descripcion"],
            "peticion": construir_peticion(
                canal_id=CANAL_ID_SIMULADO,
                metrics=",".join(info["metricas"]),
                dimensions=",".join(info["dimensiones"]),
            ),
            "forma_respuesta": forma_respuesta_resulttable(
                dimensiones=info["dimensiones"],
                metricas=info["metricas"],
            ),
        }
    return contratos


def guardar_contratos(contratos: dict, nombre_archivo: str = "golazo_analytics_contratos.json") -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    ruta = os.path.join(RAW_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(contratos, f, ensure_ascii=False, indent=2)
    print(f"Contratos de la Analytics API guardados en: {ruta}")
    return ruta


if __name__ == "__main__":
    contratos = generar_contratos()
    guardar_contratos(contratos)
