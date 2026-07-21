from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI()

# 1. Evita bloqueos si la Raspberry hace la petición desde otra IP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/chat"
# OJO: Asegúrate de que el modelo coincida con el que tienes descargado (llama3 o llama3.2)
MODEL      = "llama3.2" 
historial  = []

class Peticion(BaseModel):
    mensaje:       str
    system_prompt: str  = "Eres VELA, asistente de museo."
    limpiar:       bool = False

@app.post("/chat")
async def chat(req: Peticion):
    global historial
    
    if req.limpiar:
        historial.clear()

    historial.append({"role": "user", "content": req.mensaje})

    payload = {
        "model":    MODEL,
        "messages": [
            {"role": "system", "content": req.system_prompt}
        ] + historial,
        "stream":   False,
        "options":  {
            "temperature": 0.3, # 2. Temp baja: Respuestas más directas y menos alucinaciones
            "num_predict": 100  # 3. Límite de tokens para asegurar respuestas rápidas
        }
    }

    # 4. Manejo de errores robusto: Si Ollama se cae, el servidor no arrastra a VELA
    try:
        async with httpx.AsyncClient(timeout=15.0) as client: # Timeout estricto de 15s
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status() 
            data = resp.json()

            if "error" in data:
                print(f"[Ollama Internal Error] {data['error']}")
                return {"respuesta": None}
            
            if "message" not in data:
                return {"respuesta": None}

            respuesta = data["message"]["content"].strip()
            historial.append({"role": "assistant", "content": respuesta})

            # 5. Límite estricto de memoria: Solo recordamos los últimos 10 mensajes
            if len(historial) > 10: 
                historial = historial[-10:]

            return {"respuesta": respuesta, "modelo": MODEL}

    except httpx.ConnectError:
        print("[Server Error] No se pudo conectar a Ollama local. ¿Está corriendo?")
        return {"respuesta": None}
    except httpx.TimeoutException:
        print("[Server Error] Ollama tardó demasiado en responder (Timeout).")
        return {"respuesta": None}
    except Exception as e:
        print(f"[Server Error] Fallo inesperado: {e}")
        return {"respuesta": None}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.delete("/historial")
def limpiar():
    historial.clear()
    return {"ok": True}