# context/prompt_builder.py
# Construye prompts estructurados para Ollama

from context.context_manager import GlobalContext
from context.distance_detector import Distancia

# ── Instrucciones base de VELA ────────────────────────────
SISTEMA_BASE = """Eres VELA, asistente robótico de un museo cultural en Colombia.

REGLAS ESTRICTAS:
- Máximo 2 oraciones por respuesta
- Solo hablas de temas del museo: salas, obras, servicios, navegación
- Si el visitante pregunta algo fuera del museo, redirígelo amablemente
- Nunca inventes información sobre obras o artistas
- Nunca uses asteriscos, emojis ni símbolos en tu respuesta
- Tono: amable, claro, profesional"""


def build_system_prompt(ctx: GlobalContext) -> str:
    """
    Construye el system prompt completo para Ollama
    basado en el contexto actual.
    """
    partes = [SISTEMA_BASE, ""]

    # Instrucciones del lugar
    partes.append("CONTEXTO DEL LUGAR:")
    partes.append(ctx.lugar.resumen())
    partes.append("")

    # Instrucciones de distancia
    partes.append("PROXIMIDAD DEL VISITANTE:")
    partes.append(_instruccion_distancia(ctx.distancia.distancia))
    partes.append("")

    # Instrucciones del perfil
    instrucciones = ctx.visitante.instrucciones_comunicacion()
    if instrucciones:
        partes.append("ESTILO DE COMUNICACIÓN:")
        partes.append(instrucciones)
        partes.append("")

    return "\n".join(partes)


def build_user_prompt(texto: str, ctx: GlobalContext) -> str:
    """
    Construye el mensaje del usuario con contexto adicional.
    """
    return f"El visitante dice: {texto}"


def _instruccion_distancia(distancia) -> str:
    """
    Instrucción específica según la distancia del visitante.
    Normaliza el tipo de dato (Enum o String) para evitar errores.
    """
    # Normalización: si es Enum, obtenemos el nombre, si es string, lo ponemos en mayúsculas
    if hasattr(distancia, 'name'):
        key = distancia.name
    else:
        key = str(distancia).upper()

    instrucciones = {
        "MUY_CERCA": "El visitante está muy cerca. Responde inmediatamente y de forma directa.",
        "CERCA": "El visitante está cerca. Interacción normal.",
        "MEDIA": "El visitante está a distancia media. Puedes saludar si no lo has hecho.",
        "LEJOS": "El visitante está lejos. No inicies conversación a menos que te hable.",
        "AUSENTE": "No hay visitante detectado. Espera en modo pasivo.",
    }
    
    return instrucciones.get(key, "Distancia desconocida.")
