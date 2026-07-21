# listener.py — Vosk STT: micrófono → texto en tiempo real

import json
import queue
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer

from config import (
    VOSK_MODEL_PATH, SAMPLE_RATE, BLOCK_SIZE,
    AUDIO_DEVICE, CHANNELS
)


class VoskListener:
    def __init__(self):
        print("⏳ Cargando modelo Vosk...", end=" ", flush=True)
        self.model      = Model(VOSK_MODEL_PATH)
        self.recognizer = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.recognizer.SetWords(True)
        print("✓")

        self.phrase_queue: queue.Queue[str] = queue.Queue()
        self._audio_queue: queue.Queue      = queue.Queue()
        self._running     = False
        self._thread: threading.Thread | None = None

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        self._audio_queue.put(bytes(indata))

    def _recognition_loop(self):
        while self._running:
            try:
                data = self._audio_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text   = result.get("text", "").strip()
                if text:
                    self.phrase_queue.put(text)
            else:
                partial = json.loads(self.recognizer.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    print(f"\r🎤 {partial_text:<60}", end="", flush=True)

    def start(self):
        self._running = True
        self._stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            device=AUDIO_DEVICE,
            dtype="int16",
            channels=CHANNELS,
            callback=self._audio_callback
        )
        self._stream.start()
        self._thread = threading.Thread(
            target=self._recognition_loop,
            daemon=True,
            name="vosk-recognition"
        )
        self._thread.start()
        print("🎙️  Listener activo — habla ahora\n")

    def stop(self):
        self._running = False
        if hasattr(self, "_stream"):
            self._stream.stop()
            self._stream.close()
        if self._thread:
            self._thread.join(timeout=2)

    def get_phrase(self, timeout: float = 0.1) -> str | None:
        try:
            return self.phrase_queue.get(timeout=timeout)
        except queue.Empty:
            return None


# ── Test rápido al correr el archivo directamente ─────────
if __name__ == "__main__":
    import time
    print("🎤 Prueba de listener — habla durante 10 segundos\n")
    listener = VoskListener()
    listener.start()
    end = time.time() + 10
    while time.time() < end:
        phrase = listener.get_phrase(timeout=0.2)
        if phrase:
            print(f"\r✅ Detectado: {phrase}")
    listener.stop()
    print("\n✓ Test finalizado")
