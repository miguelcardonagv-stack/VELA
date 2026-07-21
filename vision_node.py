# vision_node.py
# PROYECTO VELA - MODO RÁFAGA NATIVA
# Acoplado al sistema completo — híbrido speaker directo + Ollama
# ──────────────────────────────────────────────────────────────────────────
# Optimizado con Filtro de Altura Anatómica para evitar falsos positivos
# ──────────────────────────────────────────────────────────────────────────

import cv2
import mediapipe as mp
import threading
import time
import numpy as np
import subprocess
import shlex
import os

from config import (
    FACE_MODEL, HAND_MODEL,
    VISION_COOLDOWN, VISION_WIDTH, VISION_HEIGHT
)

BaseOptions           = mp.tasks.BaseOptions
VisionRunningMode     = mp.tasks.vision.RunningMode
FaceLandmarker        = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
HandLandmarker        = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions


class VisionNode:

    def __init__(self, callback, speaker=None):
        """
        callback → función de main.py para eventos que van a Ollama
        speaker  → GTTSSpeaker para respuestas inmediatas sin latencia
        """
        self.callback    = callback
        self.speaker     = speaker
        self._running    = False
        self._thread     = None
        self._last_event = 0
        self.COOLDOWN    = VISION_COOLDOWN
        self.width       = VISION_WIDTH
        self.height      = VISION_HEIGHT

        # ── Face Landmarker ───────────────────────────────
        face_options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=FACE_MODEL
            ),
            running_mode=VisionRunningMode.IMAGE,
            num_faces=1
        )
        self.face_detector = FaceLandmarker.create_from_options(
            face_options
        )

        # ── Hand Landmarker ───────────────────────────────
        hand_options = HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=HAND_MODEL
            ),
            running_mode=VisionRunningMode.IMAGE,
            num_hands=2,
            min_hand_detection_confidence=0.20,
            min_hand_presence_confidence=0.20
        )
        self.hand_detector = HandLandmarker.create_from_options(
            hand_options
        )

        self.ruta_temporal = "/dev/shm/vela_frame.png"
        print("📷 [VisionNode] Inicializado — Modo Rafaga Nativa.", flush=True)

    # ── Detección gestos ──────────────────────────────────

    def _mano_abierta(self, hand_landmarks) -> bool:
        dedos    = [(8,6), (12,10), (16,14), (20,18)]
        abiertos = 0
        for tip, pip in dedos:
            if hand_landmarks[tip].y < hand_landmarks[pip].y:
                abiertos += 1
        return abiertos >= 3

    def _mano_cerrada(self, hand_landmarks) -> bool:
        dedos    = [(8,6), (12,10), (16,14), (20,18)]
        cerrados = 0
        for tip, pip in dedos:
            if hand_landmarks[tip].y > hand_landmarks[pip].y:
                cerrados += 1
        return cerrados >= 3

    def _hay_cara(self, face_result) -> bool:
        return (
            face_result and
            face_result.face_landmarks and
            len(face_result.face_landmarks) > 0
        )

    # ── Respuesta híbrida ─────────────────────────────────

    def _responder(self, evento: str):
        if evento == "stop":
            print("\n[Gesto Validado] MANO CERRADA (STOP)", flush=True)
            if self.speaker:
                self.speaker.say("Entendido, me detengo.")
            self.callback({"evento": "stop"})

        elif evento == "ayuda":
            print("\n[Gesto Validado] MANO ABIERTA (AYUDA)", flush=True)
            if self.speaker:
                self.speaker.say("¿En que te puedo ayudar?")
            self.callback({"evento": "ayuda"})

        elif evento == "persona_detectada":
            print("\nRostro detectado", flush=True)
            self.callback({"evento": "persona_detectada"})

    # ── Loop principal ────────────────────────────────────

    def _vision_loop(self):
        print("⏳ [VisionNode] Pausa estrategica 6s — esperando audio...", flush=True)
        time.sleep(6.0)

        cmd  = (
            f"rpicam-still --immediate "
            f"--width {self.width} --height {self.height} "
            f"-e png -o {self.ruta_temporal}"
        )
        args = shlex.split(cmd)

        print("🚀 [CAMARA] Canal rafaga acoplado al bus CSI.", flush=True)
        frame_count = 0

        while self._running:

            subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if not os.path.exists(self.ruta_temporal):
                time.sleep(0.05)
                continue

            frame_bgr = cv2.imread(self.ruta_temporal)
            if frame_bgr is None:
                continue

            frame_count += 1

            if frame_count == 20:
                cv2.imwrite("que_ve_vela.jpg", frame_bgr)
                print(
                    "\n📸 [DIAGNOSTICO] Imagen exportada a 'que_ve_vela.jpg'",
                    flush=True
                )

            print(
                    f"[Telemetria VELA] Cuadro: {frame_count}",
                end="\r", flush=True
            )

            frame_rgb    = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            frame_mp_rgb = cv2.flip(frame_rgb, 1)
            mp_image     = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=frame_mp_rgb
            )

            face_result = self.face_detector.detect(mp_image)
            hand_result = self.hand_detector.detect(mp_image)

            ahora      = time.time()
            cooldown_ok = (ahora - self._last_event) > self.COOLDOWN

            if cooldown_ok:
                
                y_barbilla = 1.0
                if self._hay_cara(face_result):
                    y_barbilla = face_result.face_landmarks[0][152].y

                if (hand_result.hand_landmarks and
                        len(hand_result.hand_landmarks) > 0):

                    for lista_puntos in hand_result.hand_landmarks:
                        puntos = (
                            lista_puntos.landmarks
                            if hasattr(lista_puntos, 'landmarks')
                            else lista_puntos
                        )

                        if puntos[0].y > y_barbilla:
                            continue

                        if self._mano_cerrada(puntos):
                            self._responder("stop")
                            self._last_event = ahora
                            break

                        elif self._mano_abierta(puntos):
                            self._responder("ayuda")
                            self._last_event = ahora
                            break

                elif self._hay_cara(face_result):
                    self.callback({
                        "evento": "persona_detectada",
                        "data": face_result.face_landmarks # <--- AQUÍ VA LA DATA
                    })
                    self._last_event = ahora

            time.sleep(0.02)

        if os.path.exists(self.ruta_temporal):
            try:
                os.remove(self.ruta_temporal)
            except:
                pass

        self.face_detector.close()
        self.hand_detector.close()
        print(
            "\n✓ [VisionNode] Recursos liberados limpiamente.",
            flush=True
        )

    def start(self):
        self._running = True
        self._thread  = threading.Thread(
            target=self._vision_loop,
            daemon=True,
            name="vision-node"
        )
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)


if __name__ == "__main__":
    import sys

    def mi_callback(datos):
        print(
            f"CALLBACK VELA Evento: {datos['evento'].upper()}",
            flush=True
        )

    print("🚀 Iniciando prueba solitaria de VisionNode...", flush=True)

    try:
        nodo = VisionNode(callback=mi_callback)
        nodo.start()
        print(
            "\n" + "═"*60 +
            "\n    PIPELINE VISION ACTIVO\n" +
            "═"*60 + "\n",
            flush=True
        )
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo...", flush=True)
        nodo.stop()
        sys.exit(0)
