# ollama_client.py — PROYECTO VELA
# Envía peticiones al servidor FastAPI con prompt dinámico
# ─────────────────────────────────────────────────────────

import requests
import json
from config import SERVER_URL, OLLAMA_TIMEOUT

# System prompt por defecto si no se pasa contexto
SYSTEM_DEFAULT = (
    "Eres VELA, asistente robótico inclusivo de un museo en Colombia. "
    "Responde de forma muy corta, amable y directa en máximo dos oraciones. "
    "Nunca uses asteriscos, emojis ni símbolos."
)


def ask_ollama(prompt: str, contexto: str = None) -> str | None:
    """
    Envía el texto del visitante al servidor FastAPI.

    prompt   → texto del visitante (ya procesado por build_user_prompt)
    contexto → system prompt dinámico de build_system_prompt
               Si no se pasa, usa el system prompt por defecto
    """
    url     = f"{SERVER_URL}/chat"
    headers = {"Content-Type": "application/json"}

    payload = {
        "mensaje":       str(prompt),
        "system_prompt": contexto if contexto else SYSTEM_DEFAULT,
        "limpiar":       False
    }

    try:
        print(f"[Ollama] Enviando: '{prompt[:50]}...'", flush=True)

        response = requests.post(
            url,
            data    = json.dumps(payload),
            headers = headers,
            timeout = OLLAMA_TIMEOUT
        )
        print(f"[DEBUG] Status: {response.status_code}")
        print(f"[DEBUG] Cuerpo crudo: {response.text}")

        if response.status_code == 200:
            data      = response.json()
            respuesta = data.get("respuesta", "")
            if respuesta and respuesta.strip():
                return respuesta.strip()
            print("[Ollama] Respuesta vacía del servidor.", flush=True)
            return None

        elif response.status_code == 422:
            print(
                f"[Ollama] Error 422 — validación: {response.text}",
                flush=True
            )
            return None

        else:
            print(
                f"[Ollama] Error HTTP {response.status_code}",
                flush=True
            )
            return None

    except requests.exceptions.ConnectionError:
        print("[Ollama] Sin conexión al servidor.", flush=True)
        return None

    except requests.exceptions.Timeout:
        print("[Ollama] Timeout — servidor tardó demasiado.", flush=True)
        return None

    except Exception as e:
        print(f"[Ollama] Error inesperado: {e}", flush=True)
        return None
