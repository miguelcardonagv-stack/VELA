# context/context_manager.py
# Une todo el contexto en una sola estructura
# Cualquier módulo importa esto para obtener el estado completo

from dataclasses  import dataclass
from typing       import Optional
import json
import os

from context.place_context    import PlaceContext, get_sala, SALAS_MUSEO
from context.visitor_profile  import VisitorProfile, perfil_estandar
from context.interaction_state import InteractionState
from context.distance_detector import DistanceDetector, Distancia, ResultadoDistancia

CONTEXT_FILE = "/home/abcd/Desktop/VELA/context.json"


@dataclass
class GlobalContext:
    """
    Estado completo del sistema VELA en un momento dado.
    Se pasa a prompt_builder para construir el prompt.
    """
    lugar:       PlaceContext
    visitante:   VisitorProfile
    interaccion: InteractionState
    distancia:   ResultadoDistancia


class ContextManager:
    """
    Gestiona el contexto global de VELA.
    Punto de acceso único para todos los módulos.
    """

    def __init__(self):
        self._sala_actual   = "entrada"
        self.visitante      = perfil_estandar()
        self.interaccion    = InteractionState()
        self.distancia      = ResultadoDistancia(
            distancia   = Distancia.AUSENTE,
            descripcion = "Sin detección inicial"
        )
        self._cargar_sala()

    # ── Sala ──────────────────────────────────────────────
    def _cargar_sala(self):
        try:
            if os.path.exists(CONTEXT_FILE):
                with open(CONTEXT_FILE, 'r') as f:
                    data = json.load(f)
                    sala_leida = data.get("sala", "entrada")
                # Validar contra las claves reales de tu diccionario
                    if sala_leida in SALAS_MUSEO:
                        self._sala_actual = sala_leida
                    else:
                        self._sala_actual = "entrada"
            else:
                self._sala_actual = "entrada"
        except Exception as e:
            print(f"[ContextManager] Error de lectura JSON: {e}")
            self._sala_actual = "entrada"
    def set_sala(self, clave: str):
        """Actualiza la sala actual y persiste en disco."""
        if clave in SALAS_MUSEO:
            self._sala_actual = clave
            with open(CONTEXT_FILE, 'w') as f:
                json.dump({"sala": clave}, f)
    def get_lugar(self) -> PlaceContext:
        # SIEMPRE recargamos desde disco antes de devolver el objeto
        self._cargar_sala()
        return get_sala(self._sala_actual)

    # ── Distancia ─────────────────────────────────────────

    def actualizar_distancia(self, resultado: ResultadoDistancia):
        self.distancia = resultado

        # Actualizar estado de interacción según distancia
        if resultado.distancia == Distancia.AUSENTE:
            self.interaccion.visitante_ausente()
        else:
            self.interaccion.visitante_detectado()

    # ── Perfil ────────────────────────────────────────────

    def actualizar_perfil(self, texto: str):
        """Ajusta el perfil del visitante según su input."""
        self.visitante.ajustar_por_interaccion(texto)

    def resetear_visitante(self):
        """Llama esto cuando un nuevo visitante llega."""
        self.visitante    = perfil_estandar()
        self.interaccion  = InteractionState()

    # ── Contexto global ───────────────────────────────────

    def build_context(self) -> GlobalContext:
        """
        Retorna el estado completo actual.
        Usar esto en prompt_builder.
        """
        return GlobalContext(
            lugar       = self.get_lugar(),
            visitante   = self.visitante,
            interaccion = self.interaccion,
            distancia   = self.distancia
        )

    # ── Procesamiento de input ────────────────────────────

    def procesar_input(self, texto: str) -> tuple[bool, Optional[str]]:
        """
        Procesa el texto del visitante.
        Retorna (debe_responder, mensaje_especial)

        debe_responder = False → VELA no responde
        mensaje_especial = texto si hay una respuesta predefinida
        """
        self.actualizar_perfil(texto)

        debe_responder = self.interaccion.procesar_input(texto)

        if not debe_responder:
            # Visitante rechazó ayuda
            return False, self.interaccion.mensaje_rechazo()

        return True, None
