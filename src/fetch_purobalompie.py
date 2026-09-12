"""
Script principal de la Fase 2: extraer datos REALES y públicos del
canal @PuroBalompie mediante la YouTube Data API v3, y guardarlos
como JSON crudo en /raw para poder inspeccionar su estructura antes
de diseñar la base de datos.

Ejecución:
    python -m src.fetch_purobalompie
"""

import json
import os
from datetime import datetime

from . import config
from . import youtube_client as yt


def guardar_json(data, nombre_archivo: str):
    """Guarda cualquier estructura de datos como JSON legible en /raw."""
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    ruta = os.path.join(config.RAW_DATA_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Guardado: {ruta}")


def main():
    print(f"Conectando con la YouTube Data API v3...")
    youtube = yt.build_client()

    # 1. Metadatos y estadísticas públicas del canal
    print(f"Obteniendo datos del canal {config.TARGET_HANDLE}...")
    channel_data = yt.get_channel_by_handle(youtube, config.TARGET_HANDLE)
    guardar_json(channel_data, "purobalompie_channel.json")

    print(
        f"  -> Canal: {channel_data['snippet']['title']} | "
        f"Suscriptores: {channel_data['statistics'].get('subscriberCount')} | "
        f"Vídeos: {channel_data['statistics'].get('videoCount')} | "
        f"Vistas totales: {channel_data['statistics'].get('viewCount')}"
    )

    # 2. IDs de todos los vídeos subidos
    uploads_playlist_id = yt.get_uploads_playlist_id(channel_data)
    print("Recorriendo la playlist de subidas (puede tardar unos segundos)...")
    video_ids = yt.get_all_video_ids(youtube, uploads_playlist_id)
    print(f"  -> {len(video_ids)} vídeos encontrados")
    guardar_json(video_ids, "purobalompie_video_ids.json")

    # 3. Detalle (snippet + estadísticas) de cada vídeo, en lotes de 50
    print("Obteniendo detalle y estadísticas de cada vídeo...")
    videos_details = yt.get_videos_details(youtube, video_ids)
    guardar_json(videos_details, "purobalompie_videos_detail.json")
    print(f"  -> Detalle guardado de {len(videos_details)} vídeos")

    # 4. Metadato de control: cuándo se hizo esta extracción
    guardar_json(
        {
            "fuente": config.TARGET_HANDLE,
            "fecha_extraccion": datetime.utcnow().isoformat() + "Z",
            "total_videos": len(videos_details),
        },
        "purobalompie_metadata_extraccion.json",
    )

    print("\nExtracción completa. Revisa los archivos en /raw antes de continuar.")


if __name__ == "__main__":
    main()
