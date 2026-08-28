"""
CAPA DE DOMINIO - Servicios de Negocio
Contiene la lógica de negocio pura
"""
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Dict, Optional, List
from .models import User, UserRole, OllaComun, Donacion, SolicitudRecurso, Entrega

class AuthService:
    """Servicio de autenticación y gestión de usuarios"""
    
    def __init__(self, user_repository):
        self.user_repo = user_repository

    def register_user(self, email: str, password: str, nombre: str, 
                      role: str, telefono: str = None, 
                      dni: str = None, edad: int = None, 
                      vulnerabilidad: str = None,
                      olla_asociada_id: int = None) -> Dict:
        """Registra un nuevo usuario"""
        # Validar que el usuario no exista
        existing = self.user_repo.find_by_email(email)
        if existing:
            return {"success": False, "error": "El email ya está registrado"}
        
        if role == 'beneficiario' and olla_asociada_id is None:
            return {"success": False, "error": "Los beneficiarios deben estar asociados a una olla"}

        # Crear nuevo usuario
        hashed_password = generate_password_hash(password)
        user = User(
            email=email,
            password=hashed_password,
            nombre=nombre,
            role=role,
            telefono=telefono,
            dni=dni,         
            edad=edad,      
            vulnerabilidad=vulnerabilidad,
            olla_asociada_id=olla_asociada_id
        )
        
        print(f"DEBUG: Registrando usuario {user.nombre} con Olla ID: {user.olla_asociada_id}") #eliminar esto, ya que es solo prueba

        user_id = self.user_repo.create(user)
        return {"success": True, "user_id": user_id}

    def authenticate(self, email: str, password: str) -> Dict:
        """Autentica un usuario"""
        normalized_email = (email or '').strip().lower()
        user = self.user_repo.find_by_email(normalized_email)

        if not user:
            return {"success": False, "error": "Credenciales inválidas"}

        password_matches = False
        try:
            password_matches = check_password_hash(user.password, password)
        except ValueError:
            password_matches = user.password == password

        if not password_matches:
            return {"success": False, "error": "Credenciales inválidas"}

        if not user.activo:
            return {"success": False, "error": "Usuario inactivo"}

        return {
            "success": True,
            "user_id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "role": user.role,
            "telefono": user.telefono
        }

    def get_user(self, user_id: int) -> Optional[Dict]:
        """Obtiene los datos de un usuario"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        return {
            "id": user.id,
            "email": user.email,
            "nombre": user.nombre,
            "role": user.role,
            "telefono": user.telefono,
            "dni": user.dni,
            "edad": user.edad,
            "vulnerabilidad": user.vulnerabilidad,
            "olla_asociada_id": user.olla_asociada_id
        }


class OllaComunService:
    """Servicio de gestión de ollas comunes"""
    
    def __init__(self, olla_repository):
        self.olla_repo = olla_repository

    def create_olla(self, nombre: str, usuario_id: int, descripcion: str,
                   direccion: str, telefono: str, estado: str = None) -> Dict:
        """Crea una nueva olla común"""
        olla = OllaComun(
            nombre=nombre,
            usuario_id=usuario_id,
            descripcion=descripcion,
            direccion=direccion,
            telefono=telefono,
            estado=estado or 'activa'
        )
        olla_id = self.olla_repo.create(olla)
        return {"success": True, "olla_id": olla_id}

    def get_olla(self, olla_id: int) -> Optional[Dict]:
        """Obtiene los datos de una olla común"""
        olla = self.olla_repo.find_by_id(olla_id)
        if not olla:
            return None
        return {
            "id": olla.id,
            "nombre": olla.nombre,
            "descripcion": olla.descripcion,
            "direccion": olla.direccion,
            "telefono": olla.telefono,
            "beneficiarios_atendidos": olla.beneficiarios_atendidos,
            "estado": olla.estado,
            "fecha_creacion": olla.fecha_creacion.isoformat()
        }

    def list_ollas(self, estado: Optional[str] = None) -> List[Dict]:
        """Lista todas las ollas comunes"""
        ollas = self.olla_repo.find_all(estado)
        return [{
            "id": olla.id,
            "nombre": olla.nombre,
            "descripcion": olla.descripcion,
            "direccion": olla.direccion,
            "beneficiarios_atendidos": olla.beneficiarios_atendidos,
            "estado": olla.estado
        } for olla in ollas]

    def update_olla(self, olla_id: int, data: Dict) -> bool:
        """Actualiza una olla común"""
        return self.olla_repo.update(olla_id, data)

    def delete_olla(self, olla_id: int) -> bool:
        """Elimina una olla común"""
        return self.olla_repo.delete(olla_id)


class DonacionService:
    """Servicio de gestión de donaciones"""
    
    def __init__(self, donacion_repository):
        self.donacion_repo = donacion_repository

    def create_donacion(self, donador_id: int, olla_comun_id: int,
                       tipo_recurso: str, cantidad: float, unidad: str,
                       descripcion: str = None) -> Dict:
        """Crea una nueva donación"""
        donacion = Donacion(
            donador_id=donador_id,
            olla_comun_id=olla_comun_id,
            tipo_recurso=tipo_recurso,
            cantidad=cantidad,
            unidad=unidad,
            descripcion=descripcion
        )
        donacion_id = self.donacion_repo.create(donacion)
        return {"success": True, "donacion_id": donacion_id}

    def get_donacion(self, donacion_id: int) -> Optional[Dict]:
        """Obtiene los datos de una donación"""
        donacion = self.donacion_repo.find_by_id(donacion_id)
        if not donacion:
            return None
        return {
            "id": donacion.id,
            "donador_id": donacion.donador_id,
            "olla_comun_id": donacion.olla_comun_id,
            "tipo_recurso": donacion.tipo_recurso,
            "cantidad": donacion.cantidad,
            "unidad": donacion.unidad,
            "descripcion": donacion.descripcion,
            "estado": donacion.estado,
            "fecha_creacion": donacion.fecha_creacion.isoformat()
        }

    def approve_donacion(self, donacion_id: int) -> bool:
        """Aprueba una donación"""
        return self.donacion_repo.update(donacion_id, {"estado": "aprobada"})

    def reject_donacion(self, donacion_id: int) -> bool:
        """Rechaza una donación"""
        return self.donacion_repo.update(donacion_id, {"estado": "rechazada"})

    def list_donaciones(self, estado: Optional[str] = None, donador_id: Optional[int] = None,
                        olla_comun_id: Optional[int] = None) -> List[Dict]:
        """Lista donaciones con filtros opcionales"""
        if donador_id is not None:
            donaciones = self.donacion_repo.find_by_donador(donador_id)
        elif olla_comun_id is not None:
            donaciones = self.donacion_repo.find_by_olla(olla_comun_id)
        else:
            donaciones = self.donacion_repo.find_all(estado)

        if estado is not None and donador_id is not None:
            donaciones = [d for d in donaciones if d.estado == estado]

        return [{
            "id": d.id,
            "donador_id": d.donador_id,
            "olla_comun_id": d.olla_comun_id,
            "tipo_recurso": d.tipo_recurso,
            "cantidad": d.cantidad,
            "cantidad_str": f"{d.cantidad} {d.unidad}",
            "estado": d.estado,
            "fecha_creacion": d.fecha_creacion.isoformat()
        } for d in donaciones]


class SolicitudRecursoService:
    """Servicio de gestión de solicitudes de recursos"""
    
    def __init__(self, solicitud_repository):
        self.solicitud_repo = solicitud_repository

    def create_solicitud(self, olla_comun_id: int, tipo_recurso: str,
                        cantidad: float, unidad: str, urgencia: str,
                        descripcion: str = None) -> Dict:
        """Crea una nueva solicitud de recurso"""
        solicitud = SolicitudRecurso(
            olla_comun_id=olla_comun_id,
            tipo_recurso=tipo_recurso,
            cantidad=cantidad,
            unidad=unidad,
            urgencia=urgencia,
            descripcion=descripcion
        )
        solicitud_id = self.solicitud_repo.create(solicitud)
        return {"success": True, "solicitud_id": solicitud_id}

    def list_solicitudes(self, estado: Optional[str] = None) -> List[Dict]:
        """Lista solicitudes de recursos"""
        solicitudes = self.solicitud_repo.find_all(estado)
        return [{
            "id": s.id,
            "olla_comun_id": s.olla_comun_id,
            "tipo_recurso": s.tipo_recurso,
            "cantidad": f"{s.cantidad} {s.unidad}",
            "urgencia": s.urgencia,
            "estado": s.estado,
            "fecha_creacion": s.fecha_creacion.isoformat()
        } for s in solicitudes]

    def approve_solicitud(self, solicitud_id: int) -> bool:
        """Aprueba una solicitud"""
        return self.solicitud_repo.update(solicitud_id, {"estado": "aprobada"})
