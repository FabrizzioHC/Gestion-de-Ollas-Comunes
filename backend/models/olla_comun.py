from datetime import datetime

class OllaComun:
    def __init__(self, id=None, usuario_id=None, nombre_olla="", descripcion="", direccion="", beneficiarios_atendidos=0, estado="ACTIVA", fecha_creacion=None):
        self.id = id
        self.usuario_id = usuario_id
        self.nombre_olla = nombre_olla
        self.descripcion = descripcion
        self.direccion = direccion
        self.beneficiarios_atendidos = beneficiarios_atendidos
        self.estado = estado
        self.fecha_creacion = fecha_creacion if fecha_creacion else datetime.now()