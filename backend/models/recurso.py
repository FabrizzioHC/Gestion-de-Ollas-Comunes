from datetime import datetime

class Recurso:
    def __init__(self, id=None, olla_id=None, nombre_recurso="", cantidad=0.0, unidad_medida="", fecha_actualizacion=None):
        self.id = id
        self.olla_id = olla_id
        self.nombre_recurso = nombre_recurso
        self.cantidad = cantidad
        self.unidad_medida = unidad_medida
        self.fecha_actualizacion = fecha_actualizacion if fecha_actualizacion else datetime.now()