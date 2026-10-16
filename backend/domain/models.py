"""
CAPA DE DOMINIO - Modelos de Negocio
Contiene las entidades principales del sistema
"""
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    DONADOR = "donador"
    OLLA_COMUN = "olla_comun"
    BENEFICIARIO = "beneficiario"

class User:
    """Entidad Usuario"""
    def __init__(self, id=None, email=None, password=None, nombre=None, role=None, 
                 telefono=None, activo=True, fecha_creacion=None, 
                 dni=None, edad=None, vulnerabilidad=None, olla_asociada_id=None):
        self.id = id
        self.email = email
        self.password = password
        self.nombre = nombre
        self.role = role or UserRole.DONADOR.value
        self.telefono = telefono
        self.activo = activo
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.dni = dni
        self.edad = edad
        self.vulnerabilidad = vulnerabilidad
        self.olla_asociada_id = olla_asociada_id

class OllaComun:
    """Entidad Olla Común"""
    def __init__(self, id=None, nombre=None, usuario_id=None, descripcion=None,
                 direccion=None, telefono=None, beneficiarios_atendidos=0,
                 estado="activa", fecha_creacion=None):
        self.id = id
        self.nombre = nombre
        self.usuario_id = usuario_id
        self.descripcion = descripcion
        self.direccion = direccion
        self.telefono = telefono
        self.beneficiarios_atendidos = beneficiarios_atendidos
        self.estado = estado  # activa, inactiva, pausada
        self.fecha_creacion = fecha_creacion or datetime.now()

class Donacion:
    """Entidad Donación de Recursos"""
    def __init__(self, id=None, donador_id=None, olla_comun_id=None, tipo_recurso=None,
                 cantidad=None, unidad=None, descripcion=None, estado="pendiente",
                 fecha_creacion=None, fecha_entrega=None):
        self.id = id
        self.donador_id = donador_id
        self.olla_comun_id = olla_comun_id
        self.tipo_recurso = tipo_recurso  # alimentos, medicinas, ropa, etc
        self.cantidad = cantidad
        self.unidad = unidad  # kg, porciones, unidades, etc
        self.descripcion = descripcion
        self.estado = estado  # pendiente, aprobada, entregada, rechazada
        self.fecha_creacion = fecha_creacion or datetime.now()
        self.fecha_entrega = fecha_entrega

class SolicitudRecurso:
    """Entidad Solicitud de Recurso"""
    def __init__(self, id=None, olla_comun_id=None, tipo_recurso=None, cantidad=None,
                 unidad=None, descripcion=None, urgencia="normal", estado="pendiente",
                 fecha_creacion=None):
        self.id = id
        self.olla_comun_id = olla_comun_id
        self.tipo_recurso = tipo_recurso
        self.cantidad = cantidad
        self.unidad = unidad
        self.descripcion = descripcion
        self.urgencia = urgencia  # baja, normal, alta, critica
        self.estado = estado  # pendiente, aprobada, completada, rechazada
        self.fecha_creacion = fecha_creacion or datetime.now()

class Entrega:
    """Entidad Entrega de Recursos"""
    def __init__(self, id=None, donacion_id=None, solicitud_id=None, olla_comun_id=None,
                 cantidad_entregada=None, fecha_entrega=None, observaciones=None):
        self.id = id
        self.donacion_id = donacion_id
        self.solicitud_id = solicitud_id
        self.olla_comun_id = olla_comun_id
        self.cantidad_entregada = cantidad_entregada
        self.fecha_entrega = fecha_entrega or datetime.now()
        self.observaciones = observaciones
