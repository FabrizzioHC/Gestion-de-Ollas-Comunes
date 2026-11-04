from datetime import datetime

class Donacion:
    def __init__(self, id=None, donador_id=None, olla_id=None, mensaje="", estado="Pendiente",
                 fecha_registro=None, recurso=None, cantidad=None, unidad_medida=None):
        self.id = id
        self.donador_id = donador_id
        self.olla_id = olla_id
        self.mensaje = mensaje
        self.estado = estado
        self.fecha_registro = fecha_registro if fecha_registro else datetime.now()
        self.recurso = recurso
        self.cantidad = cantidad
        self.unidad_medida = unidad_medida