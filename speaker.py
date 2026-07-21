# speaker.py — gTTS: texto → audio (no bloqueante)
# ──────────────────────────────────────────────────────────────────────────

import io
import queue
import threading
import pygame
from gtts import gTTS
from config import TTS_LANG, TTS_SLOW

class GTTSSpeaker:
    def __init__(self):
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.init()
        print("🔊 Speaker listo", flush=True)

        self._queue = queue.Queue()
        self._thread = threading.Thread(
            target=self._playback_loop,
            daemon=True,
            name="gtts-speaker"
        )
        self._thread.start()

    def _synthesize(self, text: str) -> io.BytesIO:
        tts = gTTS(text=text, lang=TTS_LANG, slow=TTS_SLOW)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf

    def _playback_loop(self):
        while True:
            text = self._queue.get()
            if text is None:
                break
            try:
                buf = self._synthesize(text)
                pygame.mixer.music.load(buf, "mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(50)
            except Exception as e:
                print(f"\n⚠️  Speaker error: {e}", flush=True)
            finally:
                self._queue.task_done()

    def say(self, text: str):
        if text.strip():
            print(f"\n🤖 VELA: {text}", flush=True)
            self._queue.put(text)

    def stop(self):
        """Detiene la reproducción actual y limpia la cola."""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                except queue.Empty:
                    break
        except Exception:
            pass

    def is_speaking(self) -> bool:
        """Retorna si el speaker está reproduciendo audio actual."""
        try:
            if pygame.mixer.get_init():
                return pygame.mixer.music.get_busy()
        except Exception:
            pass
        return False

    def close(self):
        """Cierre y liberación limpia de recursos de Pygame."""
        try:
            self.stop()
            self._queue.put(None)
            self._thread.join(timeout=2)
            if pygame.mixer.get_init():
                pygame.mixer.quit()
        except Exception:
            pass

if __name__ == "__main__":
    import time
    s = GTTSSpeaker()
    s.say("Hola, probando el sistema limpio.")
    time.sleep(3)
    s.close()
