# config.py — parámetros centralizados

# ── Vosk ─────────────────────────────────────────────────
VOSK_MODEL_PATH   = "/home/abcd/Desktop/VELA/model"
SAMPLE_RATE       = 16000          # Hz requerido por Vosk
BLOCK_SIZE        = 4000           # frames por chunk (~250ms)
SILENCE_THRESHOLD = 0.5            # segundos de silencio para confirmar fin de frase

# ── gTTS ─────────────────────────────────────────────────
TTS_LANG          = "es"
TTS_SLOW          = False

# ── Pipeline ─────────────────────────────────────────────
WAKE_WORDS        = ["hola","vela", "robot", "asistente", "amiga", "parcera", "vecina", "oye"]   # palabras de activación opcionales
EXIT_COMMANDS     = ["salir", "terminar", "adiós", "chao"]
STOP_COMMANDS     = ["silencio", "para", "detente"]
MIN_PHRASE_LEN    = 3              # ignorar frases de menos de N caracteres
COOLDOWN_MS       = 300            # ms entre detecciones para evitar doble disparo

# ── Audio ─────────────────────────────────────────────────
AUDIO_DEVICE      = None           # None = dispositivo por defecto del sistema
CHANNELS          = 1              # mono
SERVER_URL        = "http://10.191.33.138:8000"   # ← IP de tu PC
PERFIL_USUARIO    = "standard"   # standard / wheelchair / visual / hearing
OLLAMA_TIMEOUT    = 20.0
USAR_OLLAMA       = True         # False = respuestas locales sin servidor
#vision mediapipe 
FACE_MODEL = "/home/abcd/Desktop/VELA/face_landmarker.task"
HAND_MODEL = "/home/abcd/Desktop/VELA/hand_landmarker.task"
VISION_COOLDOWN   = 3.0
VISION_WIDTH      = 640
VISION_HEIGHT     = 480
