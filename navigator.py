import time
import math
class Navigator:
    def __init__(self, motores, lcd, ctx_manager):
        self.motores = motores
        self.lcd = lcd
        self.ctx = ctx_manager
        # Usaremos nombres de salas coherentes con tu JSON
        self.salas = {"entrada": 0,"arte":10,"arte_contemporaneo": 10, "historia": 20, "ciencias": 30}

    def ir_a(self, sala_destino):
        # 1. Obtener destino y actual desde el contexto real
        destino = self.salas.get(sala_destino, 0)
        actual_nombre = self.ctx._sala_actual
        actual_val = self.salas.get(actual_nombre, 0)
        
        distancia = abs(destino - actual_val)

        if distancia == 0:
            print(f"DEBUG: Ya estoy en {sala_destino}")
            return

        print(f"DEBUG: Moviendo de {actual_val} a {destino}")

        # 2. Ejecutar movimiento
        # IMPORTANTE: Aquí solo movemos, no intentamos actualizar self.posicion_actual
        for i in range(distancia):
            self.motores.mover_tiempo("adelante", 1.0)
            time.sleep(1.2) # Esperamos a que el movimiento físico termine
            self.lcd.mostrar_evento("Navegando...", f"Paso {i+1}/{distancia}")

        # 3. Guardado final (Único punto de verdad)
        self.ctx.set_sala(sala_destino)
        self.ctx._sala_actual = sala_destino
        print(f"DEBUG: Navegación a {sala_destino} confirmada y aplicada.")
def cancelar_navegacion(self):
    self.cancelado = True # Bandera que checkea tu bucle de movimiento
    self.motores.detener()
def _actualizar_lcd_mapa(self, destino):
        # 1. Definimos el tamaño de la barra
        longitud_barra = 10
        barra = ["-"] * longitud_barra

        # 2. Evitar división por cero si estamos en entrada (0)
        if destino > 0:
            # Calculamos la posición relativa al destino actual
            # Esto hace que el asterisco recorra toda la barra
            # sin importar si vas a la sala 10 o a la 20
            pos_relativa = int((self.posicion_actual / destino) * (longitud_barra - 1))
        else:
            pos_relativa = 0

        # 3. Asegurar límites
        pos_relativa = max(0, min(pos_relativa, longitud_barra - 1))

        barra[pos_relativa] = "*"
        self.lcd.mostrar_evento("Navegando...", "[" + "".join(barra) + "]")
