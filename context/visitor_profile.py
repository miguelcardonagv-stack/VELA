# context/visitor_profile.py
# Perfil de interacción del visitante
# NO almacena diagnósticos médicos ni información sensible

from dataclasses import dataclass, field
from typing      import Optional

@dataclass
class VisitorProfile:
    """
    Características de interacción del visitante.
    Solo almacena preferencias observables de comunicación.
    Se construye dinámicamente durante la interacción.
    """

    # Preferencias de comunicación
    lenguaje_simple:           bool = False
    necesita_descripcion_visual: bool = False
    prefiere_respuestas_cortas: bool = False
    prefiere_respuestas_detalladas: bool = False

    # Contexto de visita
    grupo_escolar:    bool = False
    visitante_frecuente: bool = False
    idioma:           str  = "es"

    # Campos extensibles — agregar sin romper el resto
    notas_adicionales: list = field(default_factory=list)

    def ajustar_por_interaccion(self, texto: str):
        """
        Ajusta el perfil dinámicamente según cómo habla el visitante.
        Observa patrones sin etiquetar a la persona.
        """
        texto = texto.lower()

        # Si pide repetición o más detalle
        if any(p in texto for p in ["repite", "no entendí", "más despacio",
                                     "cómo", "explica", "qué significa"]):
            self.necesita_descripcion_visual  = True
            self.prefiere_respuestas_detalladas = True

        # Si pide brevedad
        if any(p in texto for p in ["breve", "corto", "rápido",
                                     "resumido", "solo dime"]):
            self.prefiere_respuestas_cortas = True

        # Si es grupo escolar
        if any(p in texto for p in ["niños", "estudiantes",
                                     "colegio", "escuela", "clase"]):
            self.grupo_escolar = True
            self.lenguaje_simple = True

    def instrucciones_comunicacion(self) -> str:
        """
        Genera instrucciones de comunicación para el prompt.
        """
        instrucciones = []

        if self.lenguaje_simple:
            instrucciones.append("Usa lenguaje simple y claro.")
        if self.necesita_descripcion_visual:
            instrucciones.append("Describe visualmente con detalle.")
        if self.prefiere_respuestas_cortas:
            instrucciones.append("Sé muy breve, máximo 1 oración.")
        if self.prefiere_respuestas_detalladas:
            instrucciones.append("Da explicaciones completas.")
        if self.grupo_escolar:
            instrucciones.append("Habla como si explicaras a estudiantes jóvenes.")
        if self.idioma != "es":
            instrucciones.append(f"Responde en {self.idioma}.")

        return " ".join(instrucciones) if instrucciones else "Responde de forma natural y amable."


# ── Perfil por defecto ────────────────────────────────────
def perfil_estandar() -> VisitorProfile:
    return VisitorProfile()
