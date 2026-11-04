from datetime import datetime

class Solicitud:
    def __init__(self, id=None, olla_id=None, nombre_olla="", recurso_necesitado="", cantidad_necesitada=0.0, unidad_medida="", nivel_urgencia="Normal", estado="Pendiente", fecha_solicitud=None):
        self.id = id
        self.olla_id = olla_id
        self.nombre_olla = nombre_olla  # Útil si haces un JOIN con la tabla Olla_Comun
        self.recurso_necesitado = recurso_necesitado
        self.cantidad_necesitada = cantidad_necesitada
        self.unidad_medida = unidad_medida
        self.nivel_urgencia = nivel_urgencia
        self.estado = estado
        self.fecha_solicitud = fecha_solicitud if fecha_solicitud else datetime.now()