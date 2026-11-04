from datetime import datetime

class Usuario:
    def __init__(self, id=None, email="", password_hash="", nombres="", apellidos="", rol="", telefono="", dni="", activo=True, fecha_creacion=None, intentos_fallidos=0, bloqueado_hasta=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.nombres = nombres
        self.apellidos = apellidos
        self.rol = rol
        self.telefono = telefono
        self.dni = dni
        self.activo = activo
        self.fecha_creacion = fecha_creacion if fecha_creacion else datetime.now()
        self.intentos_fallidos = intentos_fallidos
        self.bloqueado_hasta = bloqueado_hasta