
# ═══════════════════════════════════════════════════════════════

import time
import threading
import signal
import sys
import queue
import unicodedata
from typing import Optional

# ── Módulos del sistema ───────────────────────────────────
from pipeline                  import VoicePipeline
from speaker                   import GTTSSpeaker
from vision_node               import VisionNode
from ollama_client             import ask_ollama

# ── Contexto ──────────────────────────────────────────────
from context.context_manager   import ContextManager, GlobalContext
from context.distance_detector import DistanceDetector, Distancia, ResultadoDistancia
from context.prompt_builder    import build_system_prompt, build_user_prompt

# ── Hardware ──────────────────────────────────────────────
from hardware.motor_node       import MotorController
from hardware.lcd_node         import LcdController
from navigator import Navigator
# ── Config ────────────────────────────────────────────────
from config import USAR_OLLAMA, PERFIL_USUARIO

# ═══════════════════════════════════════════════════════════
# CONSTANTES Y ESTADO GLOBAL
# ═══════════════════════════════════════════════════════════

PRIORIDADES = {
    "stop": 1, "ayuda": 2, "voz": 2, "persona_detectada": 3,
}

FRASES_PROPIAS = ["sistema vela activo", "estoy lista para ayudarte", "hasta pronto", "me estoy apagando", "entendido me detengo", "en que te puedo ayudar", "estare disponible"]
COOLDOWN_SALUDO = 30.0

class EstadoSistema:
    def __init__(self):
        self._lock = threading.Lock()
        self.activo = True
        self.hablando = False
        self.apagando = False
        self._ultimo_saludo = 0.0
        self.presencia_forzada_hasta = 0.0 # <--- ESCUDO DE PRESENCIA

    def set(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def puede_saludar(self) -> bool:
        return (time.time() - self._ultimo_saludo) > COOLDOWN_SALUDO

    def registrar_saludo(self):
        with self._lock:
            self._ultimo_saludo = time.time()
    def esta_ocupado(self) -> bool:
        """
        Retorna True si el robot está realizando una tarea bloqueante
        que impide nuevas interacciones.
        """
        with self._lock:
            return self.hablando or self.navegando
estado       = EstadoSistema()
cola_eventos = queue.PriorityQueue()

# Hardware y Contexto
speaker = GTTSSpeaker()
motores = MotorController()
lcd     = LcdController()
ctx_manager       = ContextManager()
distance_detector = DistanceDetector()
nav = Navigator(motores, lcd, ctx_manager)
# ═══════════════════════════════════════════════════════════
# FUNCIONES DE COMUNICACIÓN
# ═══════════════════════════════════════════════════════════

def hablar(texto: str, lcd_l2: str = ""):
    if not texto or not estado.activo or estado.apagando or estado.hablando:
        return

    def _run():
        estado.set(hablando=True)
        lcd.mostrar_evento("VELA dice:", lcd_l2 or texto[:20])
        try:
            speaker.say(texto)
            while speaker.is_speaking(): time.sleep(0.05)
        finally:
            estado.set(hablando=False)
            _actualizar_lcd_escuchando()

    threading.Thread(target=_run, daemon=True, name="hablar").start()
def _actualizar_lcd_escuchando():
    try:
        # Esto siempre lee el valor más reciente del contexto
        ctx = ctx_manager.build_context() 
        lugar_nombre = ctx.lugar.nombre # Asegúrate de que esto sea el nombre actualizado
        dist = "CERCA" # O tu lógica de distancia
        lcd.mostrar_estado("Escuchando...", lugar_nombre[:20], dist, "INTERACTIVO")
    except Exception as e:
        lcd.mostrar_evento("VELA activa", "Escuchando...")
def _actualizar_lcd_procesando(texto: str):
    lcd.mostrar_evento("Procesando...", texto[:20])

# ═══════════════════════════════════════════════════════════
# LÓGICA DE RESPUESTA
# ═══════════════════════════════════════════════════════════

def respuesta_local(texto: str) -> str:
    t = texto.lower()
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    lugar = ctx_manager.build_context().lugar.nombre
    
    if any(p in t for p in ["hola", "buenos"]): return f"Hola, bienvenido a {lugar}. Soy VELA. ¿En qué te puedo ayudar?"
    if any(p in t for p in ["adios", "chao"]): return "Hasta pronto. Fue un placer."
    return "No entendí bien. ¿Puedes repetirlo?"

def generar_respuesta(texto: str) -> Optional[str]:
    t = texto.lower()
    
    # Definición de conceptos (Listas)
    arte_keywords = ["arte", "la de arte", "sala de arte", "exposicion", "galeria"]
    entrada_keywords = ["entrada", "puerta principal", "inicio"]
    ir_keywords = ["ve a", "dirigete a", "vamos a", "vámonos a", "muevete a", "desplazate a"]

    # Lógica de detección (usando 'any' directamente)
    if any(k in t for k in ir_keywords):
        if any(a in t for a in arte_keywords):
            procesar_comando_movimiento("arte")
            ctx_manager._cargar_sala()
            return "¡Entendido! Ponemos rumbo a la sala de arte."
        if any(e in t for e in entrada_keywords):
            procesar_comando_movimiento("entrada")
            return "Claro, regreso a la entrada principal."

    # Si no detectó movimiento, sigue el flujo normal
    debe_responder, mensaje_especial = ctx_manager.procesar_input(texto)
    if not debe_responder: return mensaje_especial
    if USAR_OLLAMA:
        try:
            ctx = ctx_manager.build_context()
            respuesta = ask_ollama(build_user_prompt(texto, ctx), contexto=build_system_prompt(ctx))
            if respuesta and respuesta.strip(): return respuesta
        except: pass
    return respuesta_local(texto)
# ═══════════════════════════════════════════════════════════
# PROCESADOR DE COLA
# ═══════════════════════════════════════════════════════════
def procesar_cola():
    print("[INFO] Procesador de eventos iniciado.")
    while not estado.apagando:
        try:
            # 1. Espera de evento con timeout para permitir checkeo de estado.apagando
            try:
                # Si cambiaste la tupla en handle_vision a (prioridad, time, evento, datos),
                # asegúrate de ajustar este desempaquetado. 
                # Si sigues usando (prioridad, evento, datos), déjalo así:
                # Dentro de procesar_cola, cambia esta línea:
                prioridad, timestamp, evento, datos = cola_eventos.get(timeout=0.5)
            except queue.Empty:
                continue

            # 2. Validación de estado antes de ejecutar
            if not estado.activo:
                cola_eventos.task_done()
                continue

            # 3. Lógica de ejecución por tipo de evento
            if evento == "stop":
                motores.detener()
                nav.cancelar_navegacion()
                speaker.stop()
                hablar("Entendido, me detengo.", lcd_l2="Detenido")
                lcd.mostrar_evento("STOP", "Robot detenido")

            elif evento == "ayuda":
                if not estado.hablando: 
                    hablar("¿En qué te puedo ayudar?", lcd_l2="Ayuda solicitada")

            elif evento == "voz":
                texto = datos.get("texto", "")
                if texto and not estado.hablando:
                    estado.presencia_forzada_hasta = time.time() + 10.0
                    _actualizar_lcd_procesando(texto)
                    res = generar_respuesta(texto)
                    if res: hablar(res, lcd_l2=texto[:20])

            elif evento == "persona_detectada":
                # Filtro: Si estamos navegando o hablando, ignoramos la visión
                if not estado.hablando:
                    landmarks = datos.get("data")
                    res_dist = distance_detector.procesar_marcadores_directos(pose_landmarks=None, face_landmarks=landmarks)
                    
                    # Lógica de escudo
                    if time.time() < estado.presencia_forzada_hasta:
                        dist_str = "CERCA"
                    else:
                        dist_str = str(res_dist.distancia).upper()
                    
                    ctx_manager.distancia.distancia = dist_str
                    lcd.mostrar_estado("VELA activa", "Entrada", dist_str, "INTERACTIVO")

                    # Saludo proactivo
                    if not (dist_str == "LEJOS" or not ctx_manager.interaccion.debe_saludar_proactivamente() or not estado.puede_saludar()):
                        estado.presencia_forzada_hasta = time.time() + 10.0
                        ctx_manager.distancia.distancia = "CERCA"
                        ctx = ctx_manager.build_context()
                        res = generar_respuesta(f"saluda brevemente al visitante en {ctx.lugar.nombre}")
                        if res:
                            estado.registrar_saludo()
                            hablar(res, lcd_l2="Visitante detectado")

        except Exception as e:
            print(f"[ERROR] Error inesperado en procesar_cola: {e}")
        
        finally:
            # 4. Aseguramos que siempre se marque la tarea como terminada
            try:
                cola_eventos.task_done()
            except ValueError:
                # Esto ocurre si se llama a task_done más veces que a put
                pass
# ═══════════════════════════════════════════════════════════
# CALLBACKS Y APAGADO
# ═══════════════════════════════════════════════════════════
def handle_vision(deteccion: dict):
    # Si VELA está apagada, apagándose, hablando o navegando, ignoramos la visión
    if not estado.activo or estado.apagando or estado.esta_ocupado():
        return

    # Escudo: Si la cola ya tiene eventos pendientes, ignoramos nuevas detecciones
    # para evitar que el procesamiento de visión se acumule y genere lag.
    if cola_eventos.qsize() > 2:
        return

    evento = deteccion.get("evento", "desconocido")
    prioridad = PRIORIDADES.get(evento, 99)
    
    # Insertamos con timestamp para desempate en la PriorityQueue
    # Esto elimina el error TypeError al comparar diccionarios
    try:
        cola_eventos.put((prioridad, time.time(), evento, deteccion))
    except Exception as e:
        print(f"[ERROR] Fallo al encolar evento de visión: {e}")
def procesar_comando_movimiento(sala: str):
    # 1. Notificación inicial
    hablar(f"Entendido, me estoy desplazando a la sala {sala}", lcd_l2="Navegando...")
    
    # 2. Esperar a que la voz termine antes de mover motores
    while estado.hablando:
        time.sleep(0.1)
        
    # 3. Bloqueo de seguridad: marcamos que estamos navegando
    estado.set(navegando=True)
    
    try:
        # Navegación bloqueante (ejecuta el movimiento ahora)
        nav.ir_a(sala)
    except Exception as e:
        print(f"[ERROR] Fallo durante la navegación a {sala}: {e}")
    finally:
        # 4. Liberamos el escudo: el robot vuelve a estar disponible
        estado.set(navegando=False)
        # Opcional: Actualizar el LCD para indicar que el robot está libre
        _actualizar_lcd_escuchando()
def handle_voz(texto: str) -> Optional[str]:
    if not estado.activo or estado.apagando or estado.hablando: return None
    if any(f in texto.lower() for f in FRASES_PROPIAS): return None

    ctx_manager.distancia.distancia = "CERCA"
    ctx_manager.interaccion.visitante_detectado()

    # CAMBIO: Incluir time.time() para mantener la estructura de 4 elementos
    cola_eventos.put((PRIORIDADES["voz"], time.time(), "voz", {"texto": texto}))
    return None
def apagar(vision: VisionNode, *args):
    if estado.apagando: return
    estado.set(apagando=True, activo=False)
    lcd.mostrar_evento("Apagando...", "Hasta pronto")
    try: 
        speaker.say("Hasta pronto.")
        time.sleep(2)
    except: pass
    motores.close()
    vision.stop()
    distance_detector.close()
    speaker.close()
    lcd.limpiar()
    sys.exit(0)

if __name__ == "__main__":
    lcd.barra_progreso(0, "Iniciando VELA...")
    threading.Thread(target=procesar_cola, daemon=True, name="cola-eventos").start()
    
    vision = VisionNode(callback=handle_vision, speaker=speaker)
    vision.start()
    
    signal.signal(signal.SIGINT, lambda s, f: apagar(vision))
    signal.signal(signal.SIGTERM, lambda s, f: apagar(vision))

    pipeline = VoicePipeline(on_phrase=handle_voz)
    lcd.barra_progreso(100, "Sistema listo!")
    hablar("Sistema VELA activo. Estoy lista para ayudarte.")
    
    try: pipeline.run()
    finally: apagar(vision)
