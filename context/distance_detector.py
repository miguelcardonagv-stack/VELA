# context/distance_detector.py
# PROYECTO VELA 
import numpy as np
from enum import Enum

class Distancia(Enum):
    MUY_CERCA = "MUY_CERCA"
    CERCA     = "CERCA"
    LEJOS     = "LEJOS"
    AUSENTE   = "AUSENTE"

class ResultadoDistancia:
    """ 
    Clase puente de compatibilidad absoluta.
    Acepta argumentos y valida que la distancia sea un valor permitido.
    """
    def __init__(self, distancia=Distancia.AUSENTE, *args, **kwargs):
        # 1. Obtenemos el valor raw (string)
        valor_recibido = distancia.value if hasattr(distancia, 'value') else distancia
        
        # 2. Validación Robusta (Opción A):
        # Comparamos si el valor está dentro de los permitidos en el Enum
        if valor_recibido in [d.value for d in Distancia]:
            self.distancia = valor_recibido
        else:
            # Si llega algo corrupto como "MEDIA", forzamos a AUSENTE y avisamos al log
            print(f"[Seguridad] ALERTA: Se intentó asignar una distancia inválida: '{valor_recibido}'. Forzando estado AUSENTE.")
            self.distancia = Distancia.AUSENTE.value
        
        # Mapea dinámicamente argumentos extras que exija el constructor antiguo
        self.descripcion = kwargs.get('descripcion', str(self.distancia))
        self.ancho_hombros = kwargs.get('ancho_hombros', 0.0)


class DistanceDetector:
    def __init__(self, umbral_cerca=140.0, umbral_muy_cerca=380.0):
        """
        Calibración basada en el ancho en píxeles de los hombros (MediaPipe Pose)
        o en el ancho facial (MediaPipe Face) para máxima inclusión.
        """
        self.umbral_cerca     = umbral_cerca
        self.umbral_muy_cerca = umbral_muy_cerca
        
        # Historial para promedio móvil (Suaviza las lecturas evitando saltos locos)
        self.historial_ancho = []
        self.max_historial   = 5 
        
        # Estado actual y protección contra falsos positivos (Histeresis)
        self.estado_actual   = Distancia.AUSENTE
        self.cuadros_ausente = 0
        self.limite_ausente  = 4  # Cuadros seguidos en blanco antes de declarar AUSENTE

    def detectar(self, mp_image) -> ResultadoDistancia:
        """
        Mapeo por compatibilidad con firmas de llamada externas en main.py.
        """
        estado = self._procesar_ausencia()
        return ResultadoDistancia(distancia=estado)
    def procesar_marcadores_directos(self, pose_landmarks, face_landmarks=None) -> ResultadoDistancia:
        """
        Flujo corregido: Si la pose falla (por baja confianza o mala visibilidad),
        intentamos inmediatamente con el rostro antes de declarar AUSENTE.
        """

        # 1. Intentar con Pose
        if pose_landmarks and len(pose_landmarks) > 0:
            puntos = pose_landmarks[0] if isinstance(pose_landmarks, list) else pose_landmarks
            try:
                hombro_izq = puntos[11]
                hombro_der = puntos[12]

                # Bajamos la exigencia de confianza a 0.3 para evitar que se rinda tan rápido
                visibilidad_minima = 0.3

                if (hasattr(hombro_izq, 'presence') and hombro_izq.presence >= visibilidad_minima) and \
                   (hasattr(hombro_der, 'presence') and hombro_der.presence >= visibilidad_minima):

                    ancho_hombros = np.sqrt((hombro_izq.x - hombro_der.x)**2 + (hombro_izq.y - hombro_der.y)**2) * 640
                    return self._filtrar_y_clasificar(ancho_hombros)

                # Si llega aquí es que detectó pose pero con baja confianza: NO retornamos, dejamos que pase al rostro.
            except (IndexError, AttributeError):
                pass

        # 2. Si la pose falló o fue ignorada, intentamos con el Rostro
        if face_landmarks and len(face_landmarks) > 0:
            puntos_rostro = face_landmarks[0]
            try:
                pómulo_izq = puntos_rostro[234]
                pómulo_der = puntos_rostro[454]

                ancho_rostro = np.sqrt((pómulo_izq.x - pómulo_der.x)**2 + (pómulo_izq.y - pómulo_der.y)**2) * 640
                ancho_compensado = ancho_rostro * 2.8

                return self._filtrar_y_clasificar(ancho_compensado)
            except Exception as e:
                # ESTO ES LO QUE NECESITAMOS VER
                print(f"[DEBUG CRÍTICO] Error al procesar rostro: {type(e).__name__} - {e}", flush=True)
                # Opcional: imprimir el tipo de objeto para ver qué trae realmente
                # print(f"[DEBUG] Tipo de puntos_rostro: {type(puntos_rostro)}", flush=True)
        # 3. Solo si NINGUNO de los anteriores funcionó, declaramos AUSENTE
        return ResultadoDistancia(distancia=self._procesar_ausencia())
    def _filtrar_y_clasificar(self, ancho_medido) -> ResultadoDistancia:
        """ Aplica el promedio móvil y clasifica el estado en base a los umbrales """
        print(f"[DEBUG] Ancho detectado: {ancho_medido:.2f}", flush=True)
        self.cuadros_ausente = 0  # Reseteamos el contador ya que sí hay una persona presente
        self.historial_ancho.append(ancho_medido)
        
        if len(self.historial_ancho) > self.max_historial:
            self.historial_ancho.pop(0)
            
        # Calculamos la media de los últimos cuadros para estabilizar la lectura
        ancho_filtrado = sum(self.historial_ancho) / len(self.historial_ancho)

        # Clasificación por rangos limpios
        if ancho_filtrado >= self.umbral_muy_cerca:
            self.estado_actual = Distancia.MUY_CERCA
        elif ancho_filtrado >= self.umbral_cerca:
            self.estado_actual = Distancia.CERCA
        else:
            self.estado_actual = Distancia.LEJOS
            
        return ResultadoDistancia(distancia=self.estado_actual, ancho_hombros=ancho_medido)

    def _procesar_ausencia(self) -> Distancia:
        """ Manejo defensivo contra oclusiones o cuadros vacíos """
        self.cuadros_ausente += 1
        # Solo si pasa el límite de cuadros en blanco, vaciamos el buffer y declaramos AUSENTE
        if self.cuadros_ausente >= self.limite_ausente:
            self.historial_ancho.clear()
            self.estado_actual = Distancia.AUSENTE
        return self.estado_actual

    def close(self):
        """ Limpieza absoluta de memoria del colector """
        self.historial_ancho.clear()
        self.estado_actual = Distancia.AUSENTE
