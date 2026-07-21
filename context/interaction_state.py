# context/interaction_state.py — versión corregida

import time
import unicodedata
from dataclasses import dataclass, field
from typing      import Optional

FRASES_RECHAZO = [
    "no gracias",
    "estoy bien",
    "solo estoy mirando",
    "no necesito ayuda",
    "dejame ver",
    "gracias no",
    "no hace falta",
    "no por ahora",
    "tranquilo",
    "no te preocupes",
    "estoy bien gracias",
    "no necesito",
    "no quiero",
    "solo miro",
    "voy bien",
    "no por favor",
]

TIEMPO_PASIVO_DEFAULT = 120.0


@dataclass
class InteractionState:

    estado:         str   = "ausente"
    tiempo_pasivo:  float = TIEMPO_PASIVO_DEFAULT
    _inicio_pasivo: float = field(default=0.0, repr=False)

    def visitante_detectado(self):
        if self.estado == "ausente":
            self.estado = "activo"

    def visitante_ausente(self):
        self.estado         = "ausente"
        self._inicio_pasivo = 0.0

    def procesar_input(self, texto: str) -> bool:
        """
        True  → VELA debe responder
        False → VELA permanece en silencio
        """
        texto_norm = self._normalizar(texto)

        # Verificar rechazo
        if self._es_rechazo(texto_norm):
            self._entrar_modo_pasivo()
            print(
                f"[VELA] Modo pasivo activado por: '{texto}'",
                flush=True
            )
            return False

        # En modo pasivo — cualquier input del visitante
        # significa que quiere interactuar de nuevo
        if self.estado == "pasivo":
            print("[VELA] Visitante habló en pasivo → saliendo", flush=True)
            self._salir_modo_pasivo()
            return True

        return True

    def debe_saludar_proactivamente(self) -> bool:
        if self.estado == "pasivo":
            if self._pasivo_expiro():
                self._salir_modo_pasivo()
                return True
            return False
        return self.estado == "activo"

    def mensaje_rechazo(self) -> str:
        return "Entendido. Estaré disponible si necesitas algo."

    # ── Métodos privados ──────────────────────────────────

    def _normalizar(self, texto: str) -> str:
        """
        Normaliza el texto para comparación robusta.
        Elimina acentos, convierte a minúsculas.
        """
        texto = texto.lower().strip()
        texto = ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
        return texto

    def _es_rechazo(self, texto_norm: str) -> bool:
        """
        Verifica si el texto contiene una frase de rechazo.
        Usa texto ya normalizado.
        """
        # Normalizar también las frases de rechazo
        for frase in FRASES_RECHAZO:
            frase_norm = self._normalizar(frase)
            if frase_norm in texto_norm:
                print(
                    f"[VELA] Frase de rechazo detectada: '{frase}'",
                    flush=True
                )
                return True
        return False

    def _entrar_modo_pasivo(self):
        self.estado         = "pasivo"
        self._inicio_pasivo = time.time()

    def _salir_modo_pasivo(self):
        self.estado         = "activo"
        self._inicio_pasivo = 0.0

    def _pasivo_expiro(self) -> bool:
        if self._inicio_pasivo == 0.0:
            return True
        transcurrido = time.time() - self._inicio_pasivo
        print(
            f"[VELA] Tiempo en pasivo: {transcurrido:.0f}s "
            f"/ {self.tiempo_pasivo:.0f}s",
            flush=True
        )
        return transcurrido > self.tiempo_pasivo
