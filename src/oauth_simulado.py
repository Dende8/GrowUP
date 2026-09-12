"""
Fase 3 - Simulación del acceso OAuth delegado (rol "Analista" en Studio).

Este script NO se conecta a ningún servidor real de Google: genera un
JSON con la MISMA forma que tendría el token OAuth 2.0 que el dueño
de Golazo concedería a GrowUP en un escenario real, para poder
documentar y testar el resto del pipeline sin necesitar credenciales
reales ni acceso al canal.

En un caso real, este JSON lo generaría la librería
google-auth-oauthlib tras el flujo de consentimiento explícito del
propietario del canal (nunca contendría credenciales inventadas).

Ejecución:
    python -m src.oauth_simulado
"""

import json
import os
import secrets
from datetime import datetime, timedelta, timezone

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "raw")

# Mismos scopes que se explicaron en la Fase 0 de este proyecto
SCOPES_SOLICITADOS = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def generar_token_simulado(canal_id: str = "GOLAZO_CHANNEL_ID_SIMULADO") -> dict:
    """
    Construye un diccionario con la MISMA forma que un token real
    devuelto por el flujo OAuth 2.0 de Google, pero con valores
    generados aleatoriamente (nunca credenciales reales).
    """
    ahora = datetime.now(timezone.utc)
    return {
        "token_type": "Bearer",
        "access_token": f"SIMULADO_{secrets.token_hex(16)}",
        "refresh_token": f"SIMULADO_REFRESH_{secrets.token_hex(16)}",
        "expires_in": 3599,
        "expiry": (ahora + timedelta(seconds=3599)).isoformat(),
        "scopes_concedidos": SCOPES_SOLICITADOS,
        "canal_autorizado": {
            "channel_id": canal_id,
            "channel_title": "Golazo",
            "rol_concedido": "Analista",
        },
        "fecha_simulacion": ahora.isoformat(),
        "nota": (
            "Token SIMULADO para el proyecto académico GrowUP. "
            "En un caso real, este JSON lo generaría google-auth-oauthlib "
            "tras el consentimiento explícito del propietario del canal, "
            "y access_token/refresh_token serían valores reales emitidos "
            "por Google, nunca visibles ni compartidos como contraseña."
        ),
    }


def guardar_token(token: dict, nombre_archivo: str = "golazo_oauth_token_simulado.json") -> str:
    os.makedirs(RAW_DIR, exist_ok=True)
    ruta = os.path.join(RAW_DIR, nombre_archivo)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(token, f, ensure_ascii=False, indent=2)
    print(f"Token simulado guardado en: {ruta}")
    return ruta


if __name__ == "__main__":
    token = generar_token_simulado()
    guardar_token(token)
