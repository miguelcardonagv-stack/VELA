from gpiozero import OutputDevice
import time
import queue
import threading

class MotorController:
    def __init__(self):
        # Usar active_high=True explícitamente para mayor estabilidad
        self.ia1 = OutputDevice(17, active_high=True, initial_value=False)
        self.ia2 = OutputDevice(22, active_high=True, initial_value=False)
        self.ib1 = OutputDevice(23, active_high=True, initial_value=False)
        self.ib2 = OutputDevice(24, active_high=True, initial_value=False)
        
        self.cola_movimientos = queue.Queue()
        self._detener_loop = False
        
        self.hilo_worker = threading.Thread(target=self._worker, daemon=True, name="MotorWorker")
        self.hilo_worker.start()

    def _worker(self):
        while not self._detener_loop:
            try:
                # Timeout corto para permitir chequeo de self._detener_loop
                direccion, segundos = self.cola_movimientos.get(timeout=0.1)
                self._ejecutar_movimiento_fisico(direccion, segundos)
                self.cola_movimientos.task_done()
            except queue.Empty:
                continue

    def _ejecutar_movimiento_fisico(self, direccion, segundos):
        # Lógica idéntica a tu script de prueba exitoso
        if direccion == "adelante":
            self.ia1.on(); self.ia2.off(); self.ib1.on(); self.ib2.off()
        elif direccion == "atras":
            self.ia1.off(); self.ia2.on(); self.ib1.off(); self.ib2.on()
        # ... (mantener otras direcciones)
        
        time.sleep(segundos)
        
        # Siempre asegurar apagado al terminar
        self.ia1.off(); self.ia2.off(); self.ib1.off(); self.ib2.off()

    def detener(self):
        # Limpiar la cola de forma segura
        while not self.cola_movimientos.empty():
            try: self.cola_movimientos.get_nowait()
            except queue.Empty: break
        # Estado de reposo inmediato
        self.ia1.off(); self.ia2.off(); self.ib1.off(); self.ib2.off()

    def close(self):
        self._detener_loop = True
        self.detener()
        # Cerrar es vital para la WRO (libera los pines para otras tareas)
        for pin in [self.ia1, self.ia2, self.ib1, self.ib2]:
            pin.close()
    def mover_tiempo(self, direccion: str, segundos: float):
        print(f"[DEBUG] Orden recibida en cola: {direccion} por {segundos}s")
        self.cola_movimientos.put((direccion, segundos))

