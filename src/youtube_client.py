"""
Funciones reutilizables para hablar con la YouTube Data API v3.

Todas las funciones reciben el objeto "youtube" ya construido
(ver build_client) para no reconstruirlo en cada llamada.
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from . import config


def build_client():
    """Crea el cliente de la API autenticado con la API key (solo lectura pública)."""
    return build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)


def get_channel_by_handle(youtube, handle: str) -> dict:
    """
    Recupera metadatos y estadísticas públicas de un canal a partir
    de su @handle (p. ej. "PuroBalompie", sin la @).

    Devuelve el primer item de channels.list, con "snippet",
    "statistics" y "contentDetails" (este último trae el ID de la
    playlist de "subidas" del canal, imprescindible para listar vídeos).
    """
    handle_clean = handle.lstrip("@")
    request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        forHandle=handle_clean,
    )
    response = request.execute()

    items = response.get("items", [])
    if not items:
        raise ValueError(f"No se ha encontrado ningún canal para el handle: {handle}")

    return items[0]


def get_uploads_playlist_id(channel_data: dict) -> str:
    """Extrae el ID de la playlist 'uploads' (todos los vídeos subidos)."""
    return channel_data["contentDetails"]["relatedPlaylists"]["uploads"]


def get_all_video_ids(youtube, uploads_playlist_id: str) -> list[str]:
    """
    Recorre TODA la playlist de subidas paginando con nextPageToken
    y devuelve la lista completa de video IDs del canal.

    Coste: 1 unidad de cuota por página (hasta 50 vídeos por página).
    """
    video_ids = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


def get_videos_details(youtube, video_ids: list[str]) -> list[dict]:
    """
    Recupera snippet + statistics + contentDetails para una lista de
    video IDs, en lotes de 50 (el máximo permitido por llamada).

    Coste: 1 unidad de cuota por lote de hasta 50 vídeos.
    """
    all_details = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch),
        )
        response = request.execute()
        all_details.extend(response.get("items", []))

    return all_details


def safe_execute(request):
    """Envoltorio para capturar errores de cuota o de la API sin romper el flujo."""
    try:
        return request.execute()
    except HttpError as e:
        print(f"Error al llamar a la API: {e}")
        return None
