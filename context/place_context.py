# context/place_context.py
# Representa el entorno físico donde está VELA

from dataclasses import dataclass, field
from typing      import List

@dataclass
class PlaceContext:
    """
    Describe el lugar donde se encuentra VELA en este momento.
    Se actualiza cuando el operador cambia la sala desde el panel web.
    """
    nombre:         str
    descripcion:    str
    salas_cercanas: List[str] = field(default_factory=list)
    servicios:      List[str] = field(default_factory=list)

    def resumen(self) -> str:
        """
        Texto compacto para incluir en el prompt de Ollama.
        """
        partes = [
            f"Sala actual: {self.nombre}.",
            f"Descripción: {self.descripcion}.",
        ]
        if self.salas_cercanas:
            partes.append(
                f"Salas cercanas: {', '.join(self.salas_cercanas)}."
            )
        if self.servicios:
            partes.append(
                f"Servicios disponibles: {', '.join(self.servicios)}."
            )
        return " ".join(partes)


# ── Salas del museo ───────────────────────────────────────
# Agrega o modifica según el museo real

SALAS_MUSEO: dict[str, PlaceContext] = {

    "entrada": PlaceContext(
        nombre         = "Entrada principal",
        descripcion    = "Punto de bienvenida al museo.",
        salas_cercanas = ["Arte contemporáneo", "Historia"],
        servicios      = ["Taquilla", "Guardarropa", "Baños"]
    ),

    "arte_contemporaneo": PlaceContext(
        nombre         = "Sala de Arte Contemporáneo",
        descripcion    = "Obras colombianas de los siglos XX y XXI.",
        salas_cercanas = ["Historia", "Fotografía"],
        servicios      = ["Baños", "Cafetería"]
    ),

    "historia": PlaceContext(
        nombre         = "Sala de Historia",
        descripcion    = "Historia de Colombia desde la época precolombina.",
        salas_cercanas = ["Arte contemporáneo", "Arqueología"],
        servicios      = ["Baños"]
    ),

    "ciencias": PlaceContext(
        nombre         = "Sala de Ciencias",
        descripcion    = "Experimentos interactivos y descubrimientos científicos.",
        salas_cercanas = ["Tecnología", "Historia"],
        servicios      = ["Baños", "Tienda"]
    ),

    "arqueologia": PlaceContext(
        nombre         = "Sala de Arqueología",
        descripcion    = "Artefactos y cultura muisca y precolombina.",
        salas_cercanas = ["Historia", "Arte contemporáneo"],
        servicios      = ["Baños"]
    ),

    "fotografia": PlaceContext(
        nombre         = "Sala de Fotografía",
        descripcion    = "Fotografía documental y artística colombiana.",
        salas_cercanas = ["Arte contemporáneo"],
        servicios      = ["Cafetería", "Baños"]
    ),
}

def get_sala(clave: str) -> PlaceContext:
    """Retorna la sala por clave o la entrada por defecto."""
    return SALAS_MUSEO.get(clave, SALAS_MUSEO["entrada"])
