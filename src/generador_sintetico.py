"""
Fase 4 - Paso 2: generar los datos sintéticos de Golazo.

Dos bloques de salida:

1. Un CATÁLOGO DE VÍDEOS sintético (equivalente a lo que la Data API
   v3 devolvería si Golazo fuera público en ese nivel de detalle),
   generado a partir de los RATIOS y FORMAS observados en los datos
   REALES de @PuroBalompie (Fase 4 - Paso 1), pero re-escalado al
   tamaño real y conocido de Golazo (14.000 suscriptores, 338 vídeos,
   creado el 11/04/2015).

2. Los 5 INFORMES DE ANALYTICS definidos como contrato en la Fase 3
   (evolucion_diaria, retencion_audiencia, demografia, trafico,
   ingresos), con las filas ("rows") ya rellenas, respetando el
   formato exacto (columnHeaders + rows) documentado por Google.

Todo lo que sale de este módulo es DATO SINTÉTICO / SIMULADO, nunca
información real del canal Golazo.
"""

import json
import os
import random
from datetime import date, datetime, timedelta

import pandas as pd

from . import base_real_purobalompie as base
from . import analytics_client as ac

SYNTHETIC_DIR = os.path.join(os.path.dirname(__file__), "..", "synthetic")
RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")

random.seed(42)  # reproducibilidad: mismos resultados en cada ejecución

# --- Datos REALES conocidos del cliente (los únicos no sintéticos) -------
GOLAZO_FECHA_CREACION = date(2015, 4, 11)
GOLAZO_TOTAL_VIDEOS = 338
GOLAZO_SUSCRIPTORES_ACTUALES = 14_000
GOLAZO_SUSCRIPTORES_GANADOS_30D = 900
GOLAZO_VISTAS_30D = 301_000

HOY = date.today()

CATEGORIAS_CONTENIDO = {
    "Seguimiento del club": 0.45,
    "Opinión post-partido": 0.25,
    "Fichajes": 0.15,
    "Afición": 0.08,
    "Curiosidades de fútbol": 0.07,
}


# ---------------------------------------------------------------------
# 1. Catálogo de vídeos sintético
# ---------------------------------------------------------------------

def _generar_fechas_publicacion(n_videos: int, inicio: date, fin: date) -> list[date]:
    """
    Distribuye n_videos fechas entre inicio y fin de forma
    aproximadamente uniforme pero con jitter aleatorio, para que no
    queden espaciadas de forma perfectamente artificial.
    """
    total_dias = (fin - inicio).days
    paso = total_dias / n_videos
    fechas = []
    cursor = 0.0
    for _ in range(n_videos):
        cursor += paso
        jitter = random.uniform(-paso * 0.3, paso * 0.3)
        dia = max(0, min(total_dias, cursor + jitter))
        fechas.append(inicio + timedelta(days=dia))
    return sorted(fechas)


def _titulo_por_categoria(categoria: str, indice: int) -> str:
    plantillas = {
        "Seguimiento del club": f"Análisis del partido - Jornada {indice}",
        "Opinión post-partido": f"Nuestra opinión tras el partido #{indice}",
        "Fichajes": f"Rumores de fichajes: novedad #{indice}",
        "Afición": f"Así vive la afición el partido #{indice}",
        "Curiosidades de fútbol": f"Curiosidad futbolística #{indice}",
    }
    return plantillas[categoria]


def generar_catalogo_videos(patrones: dict) -> pd.DataFrame:
    """
    Genera el catálogo sintético de los 338 vídeos de Golazo,
    reutilizando la FORMA de la distribución de vistas real de
    PuroBalompie (normalizada) pero re-escalada a un canal de 14.000
    suscriptores, y la duración/ratios de engagement observados.
    """
    fechas = _generar_fechas_publicacion(
        GOLAZO_TOTAL_VIDEOS, GOLAZO_FECHA_CREACION, HOY
    )

    categorias = random.choices(
        list(CATEGORIAS_CONTENIDO.keys()),
        weights=list(CATEGORIAS_CONTENIDO.values()),
        k=GOLAZO_TOTAL_VIDEOS,
    )

    # Factor de escala: ratio de SUSCRIPTORES entre Golazo y
    # PuroBalompie. Es una escala estable (no depende de un único
    # vídeo viral, a diferencia de normalizar contra el máximo de
    # vistas, que quedó demostrado como sensible a outliers y
    # apelmazaba demasiados vídeos en el suelo mínimo).
    escala = GOLAZO_SUSCRIPTORES_ACTUALES / patrones["suscriptores"]
    views_reales_purobalompie = patrones["views_absolutas"]

    filas = []
    for i, (fecha, categoria) in enumerate(zip(fechas, categorias)):
        # Bootstrap: remuestreamos un vídeo real completo (conservando
        # toda la forma de la distribución real, no solo su máximo) y
        # lo reescalamos al tamaño de audiencia de Golazo.
        views_base_real = random.choice(views_reales_purobalompie)
        views = max(80, round(views_base_real * escala * random.uniform(0.7, 1.4)))

        # Bootstrap también en duración (no gaussiana con suelo forzado):
        # la duración real de vídeos de fútbol no es simétrica (mezcla
        # de resúmenes cortos y análisis largos), así que una normal
        # con suelo apelmazaba demasiados vídeos en el mínimo, igual
        # que pasaba antes con las vistas.
        duracion_base_real = random.choice(patrones["duraciones_absolutas"])
        duracion = max(60, round(duracion_base_real * random.uniform(0.85, 1.15)))
        likes = max(0, int(views * patrones["ratio_likes_por_vista"] * random.uniform(0.7, 1.3)))
        comentarios = max(0, int(views * patrones["ratio_comentarios_por_vista"] * random.uniform(0.5, 1.5)))

        filas.append({
            "video_id": f"golazo_sint_{i:04d}",
            "titulo": _titulo_por_categoria(categoria, i + 1),
            "categoria": categoria,
            "fecha_publicacion": fecha.isoformat(),
            "duracion_segundos": duracion,
            "views_totales": views,
            "likes": likes,
            "comentarios": comentarios,
        })

    return pd.DataFrame(filas)


# ---------------------------------------------------------------------
# 2. Informes de Analytics sintéticos (siguiendo el contrato Fase 3)
# ---------------------------------------------------------------------

def _repartir_entero(total: int, pesos: list[float]) -> list[int]:
    """
    Reparte `total` en tantas partes como pesos, de forma
    proporcional, garantizando que la suma final sea EXACTAMENTE
    `total` sin nunca producir un valor negativo: el ajuste de
    redondeo se aplica siempre sobre el bucket de mayor peso (el que
    tiene margen de sobra para absorberlo), nunca sobre el más
    pequeño.
    """
    suma_pesos = sum(pesos)
    valores = [round(total * p / suma_pesos) for p in pesos]
    diferencia = total - sum(valores)
    indice_mayor = pesos.index(max(pesos))
    valores[indice_mayor] += diferencia
    return valores


def generar_informe_evolucion_diaria() -> dict:
    """
    Reparte las cifras REALES conocidas (301.000 vistas y 900
    suscriptores en 30 días) entre los últimos 30 días, con
    estacionalidad semanal (más audiencia el fin de semana, cuando
    se juegan y comentan los partidos) y ruido aleatorio.
    """
    dias = 30
    fecha_fin = HOY
    fecha_inicio = fecha_fin - timedelta(days=dias - 1)

    # Peso semanal: sábado/domingo (jornada de liga) concentran más audiencia
    pesos_semana = {0: 0.9, 1: 0.8, 2: 0.85, 3: 0.9, 4: 1.1, 5: 1.6, 6: 1.5}
    fechas = [fecha_inicio + timedelta(days=i) for i in range(dias)]
    pesos = [pesos_semana[f.weekday()] * random.uniform(0.85, 1.15) for f in fechas]

    views_por_dia = _repartir_entero(GOLAZO_VISTAS_30D, pesos)
    subs_por_dia = _repartir_entero(GOLAZO_SUSCRIPTORES_GANADOS_30D, pesos)

    rows = []
    for fecha, views_dia, subs_dia in zip(fechas, views_por_dia, subs_por_dia):
        duracion_media_vista = round(random.uniform(180, 420), 1)  # segundos
        subs_perdidos = max(0, round(subs_dia * random.uniform(0.05, 0.20)))

        rows.append([
            fecha.isoformat(),
            views_dia,
            round(views_dia * duracion_media_vista / 60),  # estimatedMinutesWatched
            duracion_media_vista,
            subs_dia,
            subs_perdidos,
        ])

    forma = ac.forma_respuesta_resulttable(
        dimensiones=["day"],
        metricas=[
            "views", "estimatedMinutesWatched", "averageViewDuration",
            "subscribersGained", "subscribersLost",
        ],
    )
    forma["rows"] = rows
    return forma


def generar_informe_retencion(df_videos: pd.DataFrame) -> dict:
    """
    Genera una curva de retención sintética para TODOS los vídeos del
    catálogo (no una muestra), siguiendo la forma típica real de
    YouTube: caída fuerte en los primeros segundos, descenso más
    suave después, y ligero repunte al final (efecto end screen).
    """
    puntos = [round(x / 20, 2) for x in range(21)]  # 0.00, 0.05, ..., 1.00
    rows = []

    for _, video in df_videos.iterrows():
        caida_inicial = random.uniform(0.35, 0.55)  # % que se pierde en el primer 5%
        for punto in puntos:
            if punto <= 0.05:
                ratio = 1.0 - caida_inicial * (punto / 0.05)
            else:
                base_decay = (1 - caida_inicial) * (0.6 ** (punto * 1.8))
                repunte = 0.03 if punto >= 0.95 else 0.0
                ratio = max(0.02, base_decay + repunte)
            ratio = round(min(1.0, ratio + random.uniform(-0.02, 0.02)), 4)
            rendimiento_relativo = round(random.uniform(-0.15, 0.15), 3)
            rows.append([video["video_id"], punto, ratio, rendimiento_relativo])

    forma = {
        "kind": "youtubeAnalytics#resultTable",
        "columnHeaders": [
            {"name": "video", "columnType": "DIMENSION", "dataType": "STRING"},
            {"name": "elapsedVideoTimeRatio", "columnType": "DIMENSION", "dataType": "FLOAT"},
            {"name": "audienceWatchRatio", "columnType": "METRIC", "dataType": "FLOAT"},
            {"name": "relativeRetentionPerformance", "columnType": "METRIC", "dataType": "FLOAT"},
        ],
        "rows": rows,
    }
    return forma


def generar_informe_demografia() -> dict:
    """
    Distribución demográfica sintética plausible para un canal de
    seguimiento de un equipo de fútbol: mayoría masculina, y
    concentración en franjas de edad 25-44.
    """
    distribucion = {
        ("18-24", "male"): 14, ("18-24", "female"): 3,
        ("25-34", "male"): 27, ("25-34", "female"): 5,
        ("35-44", "male"): 22, ("35-44", "female"): 4,
        ("45-54", "male"): 13, ("45-54", "female"): 3,
        ("55-64", "male"): 6, ("55-64", "female"): 2,
        ("65-", "male"): 1, ("65-", "female"): 0,
    }
    # Pequeño ruido manteniendo la suma en 100
    # max(0.1, ...) evita que una categoría ya pequeña (p. ej. "65-"
    # con base 0 o 1) se vuelva negativa al restarle ruido aleatorio.
    ruido = {k: max(0.1, v + random.uniform(-1, 1)) for k, v in distribucion.items()}
    total = sum(ruido.values())
    normalizado = {k: round(v / total * 100, 2) for k, v in ruido.items()}

    rows = [[edad, genero, pct] for (edad, genero), pct in normalizado.items()]

    forma = ac.forma_respuesta_resulttable(
        dimensiones=["ageGroup", "gender"], metricas=["viewerPercentage"]
    )
    forma["rows"] = rows
    return forma


def generar_informe_trafico(views_totales: int = GOLAZO_VISTAS_30D) -> dict:
    """
    Reparte las vistas totales del periodo entre fuentes de tráfico
    típicas, con predominancia de "sugeridos" y "búsqueda" en canales
    temáticos consolidados.
    """
    reparto = {
        "SUGGESTED_VIDEO": 0.38,
        "YT_SEARCH": 0.24,
        "BROWSE_FEATURES": 0.15,
        "NOTIFICATION": 0.10,
        "EXTERNAL": 0.07,
        "PLAYLIST": 0.04,
        "SHORTS": 0.02,
    }
    rows = []
    fuentes = list(reparto.items())
    pesos = [pct * random.uniform(0.9, 1.1) for _, pct in fuentes]
    views_por_fuente = _repartir_entero(views_totales, pesos)

    for (fuente, _), views_fuente in zip(fuentes, views_por_fuente):
        minutos = round(views_fuente * random.uniform(3, 6))
        rows.append([fuente, views_fuente, minutos])

    forma = ac.forma_respuesta_resulttable(
        dimensiones=["insightTrafficSourceType"],
        metricas=["views", "estimatedMinutesWatched"],
    )
    forma["rows"] = rows
    return forma


def generar_informe_ingresos(informe_evolucion: dict) -> dict:
    """
    Estima ingresos diarios sintéticos a partir de las vistas diarias
    ya generadas, usando un RPM plausible para contenido futbolístico
    en español (bajo, coherente con el relato de pérdidas económicas
    del cliente) y aplicando que no todas las vistas son monetizables.
    """
    rpm_eur_por_1000 = random.uniform(0.9, 1.6)
    ratio_vistas_monetizadas = 0.55  # no todas las vistas llevan anuncio

    rows = []
    for fila in informe_evolucion["rows"]:
        fecha, views_dia = fila[0], fila[1]
        views_monetizadas = views_dia * ratio_vistas_monetizadas
        ingreso_ads = round(views_monetizadas / 1000 * rpm_eur_por_1000, 2)
        cpm = round(rpm_eur_por_1000 * random.uniform(1.6, 2.0), 2)
        playback_cpm = round(cpm * 0.85, 2)
        rows.append([fecha, ingreso_ads, ingreso_ads, cpm, playback_cpm])

    forma = ac.forma_respuesta_resulttable(
        dimensiones=["day"],
        metricas=["estimatedRevenue", "estimatedAdRevenue", "cpm", "playbackBasedCpm"],
    )
    forma["rows"] = rows
    return forma


# ---------------------------------------------------------------------
# Orquestador
# ---------------------------------------------------------------------

def main():
    os.makedirs(SYNTHETIC_DIR, exist_ok=True)

    print("Cargando patrones reales de @PuroBalompie...")
    df_real = base.cargar_videos_purobalompie()
    patrones = base.resumen_patrones(df_real)

    print("Generando catálogo sintético de vídeos de Golazo...")
    df_catalogo = generar_catalogo_videos(patrones)
    df_catalogo.to_csv(os.path.join(SYNTHETIC_DIR, "golazo_catalogo_videos.csv"), index=False)
    print(f"  -> {len(df_catalogo)} vídeos generados. "
          f"Vistas totales (histórico sintético): {df_catalogo['views_totales'].sum():,}")

    print("Generando informe de evolución diaria (30 días)...")
    evolucion = generar_informe_evolucion_diaria()
    suma_views = sum(f[1] for f in evolucion["rows"])
    suma_subs = sum(f[4] for f in evolucion["rows"])
    print(f"  -> Suma views generadas: {suma_views} (real: {GOLAZO_VISTAS_30D})")
    print(f"  -> Suma suscriptores generados: {suma_subs} (real: {GOLAZO_SUSCRIPTORES_GANADOS_30D})")

    print("Generando informe de retención de audiencia (los 338 vídeos, sin muestreo)...")
    retencion = generar_informe_retencion(df_catalogo)

    print("Generando informe de demografía...")
    demografia = generar_informe_demografia()

    print("Generando informe de fuentes de tráfico...")
    trafico = generar_informe_trafico()

    print("Generando informe de ingresos...")
    ingresos = generar_informe_ingresos(evolucion)

    salida = {
        "evolucion_diaria": evolucion,
        "retencion_audiencia": retencion,
        "demografia": demografia,
        "trafico": trafico,
        "ingresos": ingresos,
    }
    ruta_salida = os.path.join(SYNTHETIC_DIR, "golazo_analytics_sintetico.json")
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    print(f"\nInformes sintéticos guardados en: {ruta_salida}")
    print(f"Catálogo de vídeos guardado en: {SYNTHETIC_DIR}/golazo_catalogo_videos.csv")


if __name__ == "__main__":
    main()
