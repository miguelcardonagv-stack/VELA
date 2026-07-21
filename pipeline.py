# pipeline.py — une VoskListener + GTTSSpeaker + tu lógica

import time
from typing import Callable

from listener import VoskListener
from speaker  import GTTSSpeaker
from config   import (
    EXIT_COMMANDS, STOP_COMMANDS, MIN_PHRASE_LEN,
    WAKE_WORDS, COOLDOWN_MS
)


class VoicePipeline:
    """
    Loop principal de input/output por voz.

    Uso:
        pipeline = VoicePipeline(on_phrase=mi_funcion)
        pipeline.run()

    on_phrase recibe el texto transcrito y debe retornar
    el string que el robot dirá. Si retorna None, no habla.
    """

    def __init__(self, on_phrase: Callable[[str], str | None]):
        self.on_phrase  = on_phrase
        self.listener   = VoskListener()
        self.speaker    = GTTSSpeaker()
        self._last_time = 0.0

    def _cooldown_ok(self) -> bool:
        now = time.time() * 1000
        if now - self._last_time > COOLDOWN_MS:
            self._last_time = now
            return True
        return False

    def _contains(self, text: str, words: list[str]) -> bool:
        return any(w in text for w in words)

    def run(self):
        self.listener.start()
        print("─" * 50)
        print("  Pipeline activo. Di 'salir' para terminar.")
        print("─" * 50)

        try:
            while True:
                phrase = self.listener.get_phrase(timeout=0.1)
                if not phrase:
                    continue

                # Limpiar salida parcial
                print(f"\r✅ Tú: {phrase:<60}")

                # Longitud mínima
                if len(phrase) < MIN_PHRASE_LEN:
                    continue

                # Cooldown anti-doble disparo
                if not self._cooldown_ok():
                    continue

                # Comandos de control
                if self._contains(phrase, EXIT_COMMANDS):
                    self.speaker.say("Hasta pronto.")
                    time.sleep(2)
                    break

                if self._contains(phrase, STOP_COMMANDS):
                    self.speaker.stop()
                    print("🔇 Audio detenido")
                    continue

                # Si hay wake words configuradas, filtrar
                if WAKE_WORDS:
                    if not self._contains(phrase, WAKE_WORDS):
                        continue   # ignorar si no se menciona la palabra clave
                    # Limpiar wake word del texto antes de procesar
                    for ww in WAKE_WORDS:
                        phrase = phrase.replace(ww, "").strip()

                # Callback del usuario — aquí va tu lógica
                response = self.on_phrase(phrase)
                if response:
                    self.speaker.say(response)

        except KeyboardInterrupt:
            print("\n\n⛔ Interrumpido por teclado")
        finally:
            self._shutdown()

    def _shutdown(self):
        print("\n🔄 Cerrando pipeline...")
        self.listener.stop()
        self.speaker.close()
        print("✓ Pipeline cerrado")
