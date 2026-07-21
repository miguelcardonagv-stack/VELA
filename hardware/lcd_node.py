# hardware/lcd_node.py
# PROYECTO VELA — Controlador LCD 20x4 por I2C
# ─────────────────────────────────────────────────────────

from hardware.i2c_lcd_driver import lcd
import threading
import unicodedata


class LcdController:
    """
    Controlador para pantalla LCD 20x4 por I2C.
    Maneja concurrencia con lock interno.
    Limpia tildes y caracteres especiales automáticamente.

    Líneas disponibles: 4 líneas de 20 caracteres cada una.
    """

    COLS = 20
    ROWS = 4

    # Direcciones de inicio de cada fila en el LCD 20x4
    FILA_ADDR = [0x80, 0xC0, 0x94, 0xD4]

    def __init__(self, direccion: int = 0x27):
        self._lcd  = lcd(direccion)
        self._lock = threading.Lock()
        self.limpiar()

    # ── API pública ───────────────────────────────────────

    def mostrar(self, l1: str = "", l2: str = "",
                l3: str = "", l4: str = ""):
        """
        Muestra hasta 4 líneas en el LCD.
        Cada línea se trunca a 20 caracteres.
        """
        lineas = [l1, l2, l3, l4]
        with self._lock:
            self._lcd.write(0x01, 0)        # limpiar pantalla
            threading.Event().wait(0.005)   # pausa necesaria post-clear

            for i, texto in enumerate(lineas):
                texto_limpio = self._limpiar(texto)[:self.COLS]
                texto_pad    = texto_limpio.ljust(self.COLS)
                self._lcd.write(self.FILA_ADDR[i], 0)
                for char in texto_pad:
                    self._lcd.write(ord(char), 1)

    def mostrar_evento(self, titulo: str, detalle: str = ""):
        """
        Muestra un evento con formato estándar de VELA.
        Línea 1: título centrado
        Línea 2: detalle
        Líneas 3-4: vacías
        """
        self.mostrar(
            self._centrar(titulo),
            detalle,
            "",
            ""
        )

    def mostrar_estado(self, estado: str, sala: str = "",
                       distancia: str = "", modo: str = ""):
        """
        Muestra el estado completo del sistema en las 4 líneas.
        Línea 1: estado de VELA
        Línea 2: sala actual
        Línea 3: distancia del visitante
        Línea 4: modo de interacción
        """
        self.mostrar(
            self._centrar(estado),
            f"Sala: {sala}"[:self.COLS],
            f"Dist: {distancia}"[:self.COLS],
            f"Modo: {modo}"[:self.COLS]
        )

    def barra_progreso(self, porcentaje: int, titulo: str = ""):
        """
        Muestra una barra de progreso en línea 2.
        Útil para mostrar estado de carga.
        """
        bloques = int((porcentaje / 100) * self.COLS)
        barra   = ("#" * bloques).ljust(self.COLS)
        self.mostrar(
            self._centrar(titulo),
            barra,
            f"{porcentaje}%".center(self.COLS),
            ""
        )

    def limpiar(self):
        """Limpia todas las líneas del LCD."""
        self.mostrar("", "", "", "")

    # ── Métodos privados ──────────────────────────────────

    def _limpiar(self, texto: str) -> str:
        """Elimina tildes y caracteres no ASCII."""
        nfkd = unicodedata.normalize('NFKD', str(texto))
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def _centrar(self, texto: str) -> str:
        """Centra el texto en 20 caracteres."""
        return self._limpiar(texto)[:self.COLS].center(self.COLS)
